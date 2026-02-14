from datetime import date, timedelta, timezone

from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models import Max
from django.utils import timezone
from mutagen.mp3 import MP3
from user_account_app.models import CustomUser

# Create your models here.

class Artist(models.Model):
    artist_name = models.CharField(max_length=25,null=True,blank=True)
    artist_bio = models.TextField(blank=True)
    artist_image = models.FileField(upload_to='artist_image/',blank=True)
    country = models.CharField(max_length=30,blank=True)

    def __str__(self):
        return self.artist_name
    

class Genre(models.Model):
    genre_name = models.CharField(max_length=20,default='melody')
    description =models.TextField(blank=True)

    def __str__(self):
        return self.genre_name

class Album(models.Model):
    title = models.CharField(max_length=100)
    artists=models.ManyToManyField(Artist,related_name='album_artist')
    cover_image = models.ImageField(upload_to='albums/')
    release_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
    
class Songs(models.Model):
    artist=models.ManyToManyField(Artist,related_name='songs_artist')
    genre = models.ManyToManyField(Genre,related_name='songs_genre')
    album=models.ForeignKey(Album,related_name='song_album',on_delete=models.SET_NULL,null=True, blank=True,)
    title = models.CharField(max_length=50)
    duration =models.DurationField()
    release_date = models.DateTimeField(blank=True)
    songs_file = models.FileField(upload_to='songs/',validators=[FileExtensionValidator(allowed_extensions=['mp3'])])
    cover_image = models.ImageField(upload_to='music_image/')
    lyrics=models.TextField(blank=True)
    language=models.CharField(max_length=20)
    views=models.PositiveBigIntegerField(blank=True,null=True,default=0)
    likes_count=models.PositiveBigIntegerField(blank=True,null=True,default=0)

    def __str__(self):
        return self.title
    
    def save(self,*args,**kwargs):
        super().save(*args, **kwargs)  # save file first
        if self.songs_file:
            audio=MP3(self.songs_file.path)
            self.duration=timedelta(seconds=int(audio.info.length))
            super().save(update_fields=['duration'])
            
class video_song(models.Model):
    song = models.OneToOneField(Songs,related_name='video_song',on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='video_song/',validators=[FileExtensionValidator(allowed_extensions=['mp4','mkv','webm'])],blank=True,null=True)

    def __str__(self):
        return f'video for {self.song.title}'

class Playlist(models.Model):
    user=models.ForeignKey(CustomUser,related_name="playlist_user",on_delete=models.CASCADE)
    songs=models.ManyToManyField(Songs,related_name="playlist_songs")
    playlist_name= models.CharField(max_length=30)
    description=models.TextField(null=True,blank=True)
    created_at= models.DateTimeField(auto_now_add=True)
    is_public=models.BooleanField(default=True)
    playlist_cover_image = models.ImageField(upload_to='playlist_cover_image/',null=True,blank=True)

    def __str__(self):
        return self.playlist_name

# class Song_play(models.Model):
#     user=models.ForeignKey(CustomUser,related_name='song_play_user',on_delete=models.CASCADE)
#     song=models.ForeignKey(Songs,related_name='song_play_song',on_delete=models.CASCADE)
#     play_at=models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.user.user_name,self.song.title
    
# class Playback(models.Model):
#     user=models.ForeignKey(CustomUser,related_name="playback_user",on_delete=models.CASCADE)
#     song=models.ForeignKey(Songs,related_name="playback_user",on_delete=models.CASCADE)
#     play_at=models.DateTimeField(auto_now_add=True)
#     duration_played=models.DurationField()

#     def __str__(self):
#         return f'{self.user.user_name} song name {self.song.songs} played duration {self.duration_played}'
    
# class History(models.Model):
#     user=models.ForeignKey(CustomUser,related_name='history_user',on_delete=models.CASCADE)
#     song=models.ForeignKey(Songs,related_name='histroy_song',on_delete=models.CASCADE)
#     played_at=models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering=['-played_at']

#     def __str__(self):
#         return f'{self.user.user_name} played{self.song.songs}'
    
class listen_History_Song_play_Playback(models.Model):
    user=models.ForeignKey(CustomUser,related_name='history_user',on_delete=models.CASCADE)
    song=models.ForeignKey(Songs,related_name='histroy_song',on_delete=models.CASCADE)
    played_at=models.DateTimeField(auto_now_add=True)
    days = models.DateTimeField(null=True)
    duration_played=models.DurationField()
    count = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = ['user','song','days']
        ordering=['-played_at']

    def save(self, *args, **kwargs):
        if not self.days:
            self.days = timezone.localdate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.user_name} played{self.song.title}'
    
class Queue(models.Model):
    user=models.ForeignKey(CustomUser,related_name="queue_user",on_delete=models.CASCADE)
    song =models.ForeignKey(Songs,related_name="queue_song",on_delete=models.CASCADE)
    added_at= models.DateTimeField(auto_now_add=True)
    position= models.IntegerField(blank=True,null=True)

    def save(self, *args, **kwargs):
        if self.position is None:
            with transaction.atomic():
                last_position = Queue.objects.select_for_update().filter(user=self.user).aggregate(Max('position'))['position__max'] or 0
                self.position = last_position + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.song} (Position {self.position})"

    class Meta:
        unique_together=('user','song')
        ordering=['position']

class Like(models.Model):
    user=models.ForeignKey(CustomUser,related_name="like_user",on_delete=models.CASCADE)
    song=models.ForeignKey(Songs,related_name="like_song",on_delete=models.CASCADE)
    like_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'user name {self.user.user_name} song name {self.song.title}'
    
    class Meta:
        unique_together = ('user', 'song')

class Block_songs(models.Model):
    user=models.ForeignKey(CustomUser,related_name="block_song_user",on_delete=models.CASCADE)
    song=models.ForeignKey(Songs,related_name='block_songs_song',on_delete=models.CASCADE)
    blocked_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user_name},{self.song.title}"
    
    class Meta:
        unique_together=['user','song']
