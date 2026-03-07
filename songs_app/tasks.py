from celery import shared_task
import time
from .models import *
from django.conf import settings
from django.db import transaction
import os
import subprocess
import hashlib
from datetime import timedelta


ffmpeg_path = r"C:\Users\asus\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

ffprobe_path = r"C:\Users\asus\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe"

def get_audio_duration(file_path):
    command = [
    ffprobe_path,
        "-i", file_path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=p=0"
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    seconds = float(result.stdout.strip())
    return timedelta(seconds=seconds)


def assign_checksum(file_path):
    sha256 =  hashlib.sha256()
    with open(file_path,'rb') as f:
        for chunk in iter(lambda: f.read(4096),b""):
            sha256.update(chunk)
        return sha256.hexdigest()

@shared_task(bind =True,max_retries=3)
def music_streaming(self,music_path):
    media_assets = MediaAsset.objects.select_related("song").get(id=music_path)
    # if media_assets.DoesNotExist:
    #     return "media_assets song is not exist"
    try:
       song = media_assets.song

       media_assets.processing_status = "processing"
       media_assets.save(update_fields=["processing_status"])

       input_path = media_assets.original_file.path

       chucksum = assign_checksum(input_path)
       media_assets.checksum = chucksum
       media_assets.save(update_fields=["checksum"])

       duration = get_audio_duration(input_path)
       song.duration = duration
       song.save(update_fields =['duration'])

       output_folder = os.path.join(
           settings.MEDIA_ROOT,
            f"hls/song_{song.id}"
       )

       os.makedirs(output_folder,exist_ok= True)

       playlist_path = os.path.join(output_folder,"index.m3u8")
       segment_path = os.path.join(output_folder, "segment%d.ts")

       # 🔹 FFmpeg HLS conversion (single bitrate)
       command = [
            ffmpeg_path,
            "-i", input_path,
            "-vn",
            "-c:a", "aac",
            "-b:a", "128k",
            "-hls_time", "10",
            "-hls_list_size", "0",
            "-hls_segment_filename", segment_path,
            playlist_path
       ]
       
       subprocess.run(command,check=True)

       # 🔹 Save streaming info
       hls_url = f"{settings.MEDIA_URL}hls/song_{song.id}/index.m3u8"

       with transaction.atomic():
           SongStream.objects.update_or_create(
               song=song,
               defaults={
                   "hls_master_url":hls_url,
                   "storage_provider":media_assets.storage_provider,
               }
           )

           media_assets.processing_status= "complete"
           media_assets.save(update_fields=["processing_status"])

       return "hls process is done"
    
    except Exception as e:
        media_assets.processing_status = "failed"
        media_assets.save(update_fields=["processing_status"])
        raise self.retry(countdown=5)
    