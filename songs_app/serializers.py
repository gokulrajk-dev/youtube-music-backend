from rest_framework import serializers

from user_account_app.models import *
from user_account_app.serializers import *

from .models import *


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = "__all__"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"

class AlbumSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(read_only = True,many=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset = Artist.objects.all(),
        write_only=True,
        many =True,
        source='artists'
    )
    class Meta:
        model = Album
        fields = "__all__"

class songsSerializer_writeonly(serializers.ModelSerializer):
    # # WRITE (IDs only)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        many=True,
        write_only=True,
        source='artist'
    )

    genre_id = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        write_only=True,
        source='genre'
    )

    album_id = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(),
        write_only=True,
        source='album'
    )
    class Meta:
        model = Songs
        fields = [
            'id',
            'title',

            # media
            'songs_file',
            'cover_image',

            # metadata
            'duration',
            'release_date',
            'lyrics',
            'language',
            'views',
            'likes_count',

            # write-only
            'artist_id',
            'genre_id',
            'album_id',
        ] 

class  songSerializer_readonly(serializers.ModelSerializer):
    # READ (nested)
    artist = ArtistSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Songs
        fields = [
            'id',
            'title',

            # nested READ
            'artist',
            'genre',
            'album',

            # media
            'songs_file',
            'cover_image',

            # metadata
            'duration',
            'release_date',
            'lyrics',
            'language',
            'views',
            'likes_count',

        ] 


class video_songSerialize(serializers.ModelSerializer):
    song_id = serializers.PrimaryKeyRelatedField(
        queryset= Songs.objects.all(),
        write_only = True,
        source = 'song'
    )
    class Meta:
        model= video_song
        fields =['video_file','song_id']

# producational level for this serializer used in the front end.

class video_song_in_songs(serializers.ModelSerializer):
    # video = VideoSongSerializer(source='video_song', read_only=True)
    video_song = video_songSerialize(read_only=True)
    has_video = serializers.SerializerMethodField()

    class Meta:
        model = Songs
        fields =[
            'title',
            'cover_image',
            'songs_file',
            'video_song',
            'has_video',
            'duration',
            'release_date',
            'lyrics',
            'language',
            'views',
            'likes_count',
        ]

    def get_has_video(self,obj):
        return hasattr(obj,'video_song')

class songs_for_playlist(serializers.ModelSerializer):
    artist = ArtistSerializer(many=True,read_only=True)
    album = AlbumSerializer(read_only=True)


    class Meta:
        model = Songs
        fields =[
            'artist',
            'album',
            'title',
            'duration',
            'release_date',
            'songs_file',
            'cover_image',
            'lyrics',
            'views',
            'likes_count'
        ]


# ############################################# histroy Serializer ################


class listenhistorySerializer(serializers.ModelSerializer):
    user = customusserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True,
        source='user'
    )
    song = songSerializer_readonly(read_only=True)
    songs_id=serializers.PrimaryKeyRelatedField(
        queryset = Songs.objects.all(),
        write_only=True,
        source='song'
    )
    class Meta:
        model = listen_History_Song_play_Playback
        fields ="__all__"

class queueSerializer(serializers.ModelSerializer):
    user = customusserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True,
        source='user'
    )
    song = songs_for_playlist(read_only=True,write_only=False)
    songs_id=serializers.PrimaryKeyRelatedField(
        queryset = Songs.objects.all(),
        write_only=True,
        source='song'
    )

    class Meta:
        model= Queue
        fields = "__all__"



    

class blocksongSerializer(serializers.ModelSerializer):
    user = customusserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True,
        source='user'
    )
    song = songs_for_playlist(read_only=True)
    songs_id=serializers.PrimaryKeyRelatedField(
        queryset = Songs.objects.all(),
        write_only=True,
        source='song'
    )
    class Meta:
        model = Block_songs
        fields ="__all__"













#######################################front end producation level serializer ####################################################


class pro_songs_for_playlist_like_list_api(serializers.ModelSerializer):
    artist = ArtistSerializer(many=True,read_only=True)
    # album = AlbumSerializer(read_only=True)


    class Meta:
        model = Songs
        fields =[
            'id',
            'artist',
            'title',
            'duration',
            'release_date',
            'songs_file',
            'cover_image',
            'lyrics',
            'views',
            'likes_count'
        ]



class likedSerializer(serializers.ModelSerializer):
    # user = customusserSerializer(read_only=True)
    # user auto select
    # user_id = serializers.PrimaryKeyRelatedField(
    #     queryset=CustomUser.objects.all(),
    #     write_only=True,
    #     source='user'
    # )
    song = pro_songs_for_playlist_like_list_api(read_only=True)
    songs_id=serializers.PrimaryKeyRelatedField(
        queryset = Songs.objects.all(),
        write_only=True,
        source='song'
    )

    class Meta:
        model = Like
        fields = '__all__'

#######################pro playlist####################

class playlistSerializer(serializers.ModelSerializer):
    # user = customusserSerializer(read_only=True)
    # user_id = serializers.PrimaryKeyRelatedField(
    #     queryset=CustomUser.objects.all(),
    #     write_only=True,
    #     source='user'
    # )
    songs = pro_songs_for_playlist_like_list_api(read_only=True,many=True)
    songs_id=serializers.PrimaryKeyRelatedField(
        queryset = Songs.objects.all(),
        write_only=True,
        many =True,
        source='songs'
    )
    class Meta:
        model = Playlist
        fields='__all__'