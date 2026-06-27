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

    artist = ArtistSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Songs
        fields = [
            'id',
            'title',

            # media
            
            'cover_image',
            'artist',
            'genre',
            'album',

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

# declare the song Stream for find the reverse trace using the song 
class songSStremSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongStream
        fields="__all__"

class search_song_serializer(serializers.ModelSerializer):
    class Meta:
        model = Songs
        fields =['title']

class  songSerializer_readonly(serializers.ModelSerializer):
    # READ (nested)
    stream = songSStremSerializer(read_only=True)
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
            
            'cover_image',

            # metadata
            'duration',
            'release_date',
            'lyrics',
            'language',
            'views',
            'likes_count',
            'stream',
        ]

class demo_song_seralizer(serializers.ModelSerializer):
    artist_count = serializers.IntegerField()
    class Meta:
        model = Songs
        fields =['id','title','artist_count','duration',
            'release_date',
            'lyrics',
            'language',
            'views',
            'likes_count',]

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
            
            'cover_image',
            'lyrics',
            'views',
            'likes_count'
        ]




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


# back tracking for the any model using related name 
# class pro_artist(serializers.ModelSerializer):
#     songs_artist = serializers.SerializerMethodField()

#     class Meta:
#         model = Artist
#         fields = [
#             'id',
#             'artist_name',
#             'songs_artist'
#         ]

#     def get_songs_artist(self, obj):
#         from songs_app.serializers import pro_songs_for_playlist_like_list_api
#         return pro_songs_for_playlist_like_list_api(
#             obj.songs_artist.all(),
#             many=True
#         ).data


class pro_artist(serializers.ModelSerializer):
    
    class Meta:
        model = Artist
        fields =[
            'id',
            'artist_name',
            'artist_image'
        ]

class pro_simple_album(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields=[
            'id',
            'cover_image',
            'title'
        ]


# demo for checking serializer
class pro_artist1(serializers.ModelSerializer):
    
    class Meta:
        model = Artist
        fields =[
            'id',
            'artist_name',
        ]

class pro_simple_album1(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields=[
            'id',
            'title',
            ]

# end of the checking serializer

class pro_songs_for_playlist_like_list_api(serializers.ModelSerializer):
    # for app use
    # artist = pro_artist1(many=True,read_only=True)
    # album = pro_simple_album1(read_only=True)
    artist=ArtistSerializer(many=True,read_only=True)
    album = AlbumSerializer(read_only=True)
    genre = GenreSerializer(read_only=True,many=True)

    class Meta:
        model = Songs
        fields =[
          'id',
            'title',

            # nested READ
            'artist',
            'genre',
            'album',

            # media
            
            'cover_image',

            # metadata
            'duration',
            'release_date',
            'lyrics',
            'language',
            'views',
            'likes_count',
    
        ]

class artist_song_list(serializers.ModelSerializer):
    songs_artist = pro_songs_for_playlist_like_list_api(many=True,read_only = True)

    class Meta:
        model = Artist
        fields = "__all__"

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

    

    songs_id=serializers.PrimaryKeyRelatedField(
        queryset = Songs.objects.all(),
        write_only=True,
        many =True,
        source='songs'
    )

    songs = pro_songs_for_playlist_like_list_api(read_only =True,many = True)


    class Meta:
        model = Playlist
        fields=[
            'id',
            'songs',
            'playlist_name',
            'playlist_cover_image',
            'songs_id',
        ]
        read_only_fields = ['songs']
        
# show the playlist for the RetrieveUpdateDestroyAPIView
class RetrieveUpdateDestroyplaylistSerializer(serializers.ModelSerializer):
    songs = pro_songs_for_playlist_like_list_api(read_only=True,many=True)
    class Meta:
        model = Playlist
        fields="__all__"
        


class album_for_song(serializers.ModelSerializer):
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset = Artist.objects.all(),
        many=True,
        write_only =True,
        source='artists',
    )
    song_album = pro_songs_for_playlist_like_list_api(read_only =True,many = True)
    artists = pro_artist(read_only=True,many=True)
    

    class Meta:
        model = Album
        fields = "__all__"

# ############################################# histroy Serializer ################


class listenhistorySerializer(serializers.ModelSerializer):
    # user = customusserSerializer(read_only=True)
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
        model = listen_History_Song_play_Playback
        fields ="__all__"


class demo_history_normal_serializer(serializers.Serializer):
    song = pro_songs_for_playlist_like_list_api(read_only=True,many=True)
    song_pk = serializers.IntegerField()
    total_count = serializers.IntegerField()
    total_duration = serializers.DurationField()  # ✅ correct type


# ####################################################### pro genre ######################################

# class ProGenreSerializer(serializers.ModelSerializer):
#     songs_genre= songSerializer_readonly(read_only=True,many=True)

#     class Meta:
#         model = Genre
#         fields = "__all__"


class ProGenreSerializer(serializers.ModelSerializer):
    songs_genre = songSerializer_readonly(read_only=True, many=True)
    # albums = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = "__all__"

    # def get_albums(self, obj):
    #     albums = Album.objects.filter(
    #         song_album__genre=obj
    #     ).distinct()

    #     return AlbumSerializer(albums, many=True).data


class MediaAssetsSerializer(serializers.ModelSerializer):

    song =  pro_songs_for_playlist_like_list_api(read_only=True)

    class Meta:
        model = MediaAsset
        fields ="__all__"