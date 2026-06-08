from datetime import timedelta, timezone
from warnings import filters
from django.apps import apps

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status  # type: ignore
from rest_framework import generics, viewsets
from rest_framework.authentication import (SessionAuthentication)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView  # type: ignore
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, pagination, viewsets

from .filter import *
from .models import *
from .permission import *
from .serializers import *
from .tasks import *
from user_account_app.permission import *
from django.db.models import Prefetch,Count,Sum, F

# User = get_user_model()

# return all the table 

class GetAllTable(APIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsSuperUser]
    def get(self,request):
        tables=[]
        for model in apps.get_models():
            if model._meta.app_label == "songs_app":
                tables.append(model.__name__)
        return Response(tables)


# all extra function
class OwnerStaffSuperuserQuerysetMixin:
    def set_queryset_call(self):
        raise NotImplementedError("you must use the set_queryset_call")
    
    def get_queryset(self):
        user=self.request.user
        queryset = self.set_queryset_call()

        if user.is_superuser or user.is_staff:
            return queryset
        return queryset.filter(user=user)

# crud for artist
class artist_views(viewsets.ModelViewSet):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[Issuper_user_only_other_readonly]
    queryset = Artist.objects.all()
    filter_backends=[DjangoFilterBackend,
                    filters.SearchFilter,
                    filters.OrderingFilter
                    ]
    search_fields=['artist_name']
    # serializer_class = ArtistSerializer
    def get_serializer_class(self):
        if self.request.method in ['POST','PUT','PATCH']:
            return ArtistSerializer
        if self.action == 'retrieve':
            return artist_song_list
        return pro_artist

# crud for genre

class genre_views(viewsets.ModelViewSet):
    # authentication_classes=[SessionAuthentication]
    permission_classes = [Issuper_user_only_other_readonly]
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

# crud for album

class album_views(viewsets.ModelViewSet):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[Issuper_user_only_other_readonly]
    queryset=Album.objects.all().prefetch_related('artists')
    filter_backends=[DjangoFilterBackend,
                    filters.SearchFilter,
                    filters.OrderingFilter
                    ]
    search_fields=['title']
    serializer_class=album_for_song

# crud for songs
# effiecient but not for the scalable.
# class songs_views(generics.ListAPIView):
#     authentication_classes=[SessionAuthentication]
#     permission_classes=[Issuper_user_only_other_readonly]
#     queryset = Songs.objects.all().select_related('album').prefetch_related('artist','genre','album__artists')
#     serializer_class=songSerializer_readonly

# class songs_create_views(generics.CreateAPIView):
#     authentication_classes=[SessionAuthentication]
#     permission_classes=[Issuper_user_only_other_readonly]
#     queryset = Songs.objects.all().select_related('album').prefetch_related('artist','genre','album__artists')
#     serializer_class=songsSerializer_writeonly

# efficient and scaleable.
class Song_views(viewsets.ModelViewSet):
    # authentication_classes =[SessionAuthentication]
    permission_classes=[Issuper_user_only_other_readonly]
    queryset = Songs.objects.all().select_related('album').prefetch_related('artist','genre','album__artists')
    filter_backends=[DjangoFilterBackend,
                    filters.SearchFilter,
                    filters.OrderingFilter
                    ]
    search_fields=['title','genre__genre_name']
    # pagination_class=PageNumberPagination
    # pagination_class.page_size=10

    def get_serializer_class(self):
        if self.request.method in ['POST','PUT','PATCH']:
            return songsSerializer_writeonly
        if self.action == 'retrieve':
            return songSerializer_readonly
        return pro_songs_for_playlist_like_list_api

class search_song_views(generics.ListAPIView):
    permission_classes =[Issuper_user_only_other_readonly]
    queryset =Songs.objects.all()
    serializer_class =search_song_serializer
    filter_backends=[
        filters.SearchFilter
    ]
    search_fields=['title']


class songs_edit_views(generics.RetrieveDestroyAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes =[Issuper_user_only_other_readonly]
    queryset = Songs.objects.all().select_related('album').prefetch_related('artist','genre','album__artists')
    serializer_class=songSerializer_readonly

class songs_edit_update_views(generics.UpdateAPIView):
    authentication_classes=[SessionAuthentication]
    permission_classes =[Issuper_user_only_other_readonly]
    queryset = Songs.objects.all().select_related('album').prefetch_related('artist','genre','album__artists')
    serializer_class=songsSerializer_writeonly

class songs_for_playlist_views(APIView):
    def get(self,request):
        data = Songs.objects.all().select_related('album').prefetch_related(
            'artist','genre','album__artists'
        )
        serializer = songs_for_playlist(data,many=True)
        return Response(serializer.data,200)

class song_in_video_song_views(generics.ListAPIView):
    authentication_classes=[SessionAuthentication]
    permission_classes=[Issuper_user_only_other_readonly]
    queryset = Songs.objects.all().select_related('album').prefetch_related('artist','genre')
    serializer_class = video_song_in_songs

    # create the song like the producation level

class Media_assets_in_song(APIView):
    def post(self,request):
        song_id = request.data.get("song")
        orginal_song = request.FILES.get("orginal_song")

        if not song_id and not orginal_song:
            return Response({"message":"the song_id and orginal_song must give value"})

        try:
            song = Songs.objects.get(id =song_id)

        except Songs.DoesNotExist:
            return Response({"message":"the song does not exits"},404)

        media_assets = MediaAsset.objects.create(
            song=song,
            original_file =orginal_song
        )

        music_streaming.delay(media_assets.id)

        return Response(
            {
                "message": "Song uploaded, Processing started.",
                "song_id": song.id
            },
            status=status.HTTP_201_CREATED
        )
    
class songStream_in_song_get(APIView):
    
    def get(self,request,id):
        Media_assetss = SongStream.objects.get(id=id)

        serializer = songSStremSerializer(Media_assetss)

        return Response(serializer.data)

# crud of video_song
class video_songs_views(generics.ListCreateAPIView):
    authentication_classes=[SessionAuthentication]
    permission_classes=[Issuper_user_only_other_readonly]
    queryset = video_song.objects.all()
    serializer_class = video_songSerialize
    
# crud for playlists
class playlist_views(OwnerStaffSuperuserQuerysetMixin,generics.ListCreateAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    serializer_class=playlistSerializer

    # def get_queryset(self):
    #     return (
    #       Playlist.objects.filter(user=self.request.user).select_related('user').prefetch_related('songs','songs__artist','songs__album','songs__genre','songs__album__artists')  
    #     )
    # def get(self,request):
    #     data = Playlist.objects.all().select_related('user').prefetch_related('songs','songs__artist','songs__album','songs__genre','songs__album__artists')
    #     serializer = playlistSerializer(data,many=True)
    #     return Response(serializer.data,200)

    def set_queryset_call(self):
        return (Playlist.objects.select_related('user').prefetch_related('songs','songs__artist','songs__album','songs__genre','songs__album__artists'))
    
    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)
    
class playlist_edit_views(generics.RetrieveUpdateDestroyAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    queryset =Playlist.objects.all().select_related('user').prefetch_related('songs','songs__artist','songs__album','songs__genre','songs__album__artists')
    serializer_class =RetrieveUpdateDestroyplaylistSerializer

    def post(self,request,*args ,**kwargs):
        playlist = self.get_object()
        songs_ids = request.data.get('songs_id',[])
        action =request.data.get("action")

        if action == "post":
            if not songs_ids :
                return Response({"message":"the song id not found"})
            
            exist_id = set(playlist.songs.filter(id__in = songs_ids).values_list('id',flat =True))

            nonExist = set(songs_ids) - exist_id

            if not nonExist:
                return Response({"message":"songs already added"},200)
            
            song = Songs.objects.filter(id__in = nonExist)
            playlist.songs.add(*song)
            return Response({"message":"the songs added successfully"},201)
        
        elif action =="delete":
            if not songs_ids:
                return Response({"message":"enter the song id"},404)
            exist = playlist.songs.filter(id__in = songs_ids)

            if exist:
                playlist.songs.remove(*exist)
                return Response({"message":"song delete successfully"},204)
            else:
                return Response({"message":"no songs found in the playlist"},200)
    
# crud for listen history
# measure play count , play time , add views to songs over 30 second , sort by day like
# youtube music history manage

class listen_history_views_post(APIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    def post(self,request):
        user_id = request.user
        song_id = request.data.get("songs_id")
        durations = request.data.get("duration")

        if  not song_id or not durations :
            return Response({"message":"all field is required"})
        
        
        song = get_object_or_404(Songs,id = song_id)
        durationss = timedelta(seconds=int(durations))
        # dates = timezone.localdate()
        now = timezone.now()
        dates = now.date()
            
        with transaction.atomic():
            history,created= listen_History_Song_play_Playback.objects.get_or_create(
                user=user_id,
                song=song,
                days=dates,
                defaults={'duration_played':durationss,
                'played_at' : now,
                'count':1
                }
            )
            
            if not created :
                history.duration_played += durationss
                history.played_at=now
                history.count+=1
                history.save()
    
            if int(durations) >=30:
                one_minute_ago = now - timedelta(minutes=1)

                already_count = listen_History_Song_play_Playback.objects.filter(
                    user=user_id,
                    song=song,
                    played_at__gt=one_minute_ago
                ).exclude(id=history.id).exists()

                if not already_count:
                    Songs.objects.filter(id=song.id).update(views = F('views')+1)
                    song.refresh_from_db()
                    # song.views +=1
                    # song.save(update_fields=['views'])
                
            serializer = listenhistorySerializer(history)
            return Response(serializer.data,201)
        
class listen_history_views(OwnerStaffSuperuserQuerysetMixin,generics.ListAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    serializer_class=listenhistorySerializer
    pagination_class=PageNumberPagination
    pagination_class.page_size=10
    # queryset = (
    #     listen_History_Song_play_Playback.objects
    #     .select_related(
    #         'user',
    #         'song',
    #         'song__album'
    #     )
    #     .prefetch_related(
    #         'song__artist',
    #         'song__genre',
    #         'song__album__artists'
    #     )
    # ).order_by('-played_at')
    
    def set_queryset_call(self):
        return ( listen_History_Song_play_Playback.objects
        .select_related(
            'user',
            'song',
            'song__album'
        )
        .prefetch_related(
            'song__artist',
            'song__genre',
            'song__album__artists'
        )
    ).order_by('-played_at')
    
    


class history_edit_views(OwnerStaffSuperuserQuerysetMixin,generics.RetrieveUpdateDestroyAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    # queryset = (
    #     listen_History_Song_play_Playback.objects
    #     .select_related(
    #         'user',
    #         'song',
    #         'song__album'
    #     )
    #     .prefetch_related(
    #         'song__artist',
    #         'song__genre',
    #         'song__album__artists'
    #     )
    # )
    serializer_class=listenhistorySerializer
    def set_queryset_call(self):
        return ( listen_History_Song_play_Playback.objects
        .select_related(
            'user',
            'song',
            'song__album'
        )
        .prefetch_related(
            'song__artist',
            'song__genre',
            'song__album__artists'
        )
    )



# crud for queue

class queue_views(generics.ListCreateAPIView):
    queryset = Queue.objects.all().select_related('user','song','song__album').prefetch_related('song__artist','song__genre','song__album__artists')
    serializer_class = queueSerializer


class queue_edit_views(generics.RetrieveUpdateDestroyAPIView):
    queryset = Queue.objects.all().select_related('user','song','song__album').prefetch_related('song__artist','song__genre','song__album__artists')
    serializer_class = queueSerializer

# crud of like 

class like__views_post(APIView):
    def post(self,request):
        user_id = request.data.get("user_id")
        song_id=request.data.get("song_id")
        
        user=get_object_or_404(CustomUser,id = user_id)
        song=get_object_or_404(Songs,id = song_id)

        with transaction.atomic():
            like, create = Like.objects.get_or_create(
                user=user,
                song=song
            )

            if create:
                Songs.objects.filter(id=song.id).update(likes_count = F('likes_count')+1)
                song.refresh_from_db()
                return Response({"message":"this song liked by you "},200)
            else:
                return Response({"error":"this song already liked"},400)
            
class like_and_unlike_views(APIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    def post(self,request):
        user = self.request.user
        song_id=request.data.get("song_id")
        
        song=get_object_or_404(Songs,id = song_id)

        with transaction.atomic():

            like=Like.objects.filter(user = user, song=song)

            if like.exists():
                like.delete()
                Songs.objects.filter(id=song.id).update(likes_count=F('likes_count')-1)
                song.refresh_from_db()
                return Response({"message":"this song disliked by you "},200)
                

            Like.objects.create(user=user,song=song)
            Songs.objects.filter(id=song.id).update(likes_count=F('likes_count')+1)
            song.refresh_from_db()
            return Response({
                'song_count':song.likes_count
            },200)
        

# auto select the user
# class list_create(generics.CreateAPIView):
#     permission_classes=[IsOwnerAndSuperuserOnly]
#     serializer_class =likedSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user) 



class like_views(OwnerStaffSuperuserQuerysetMixin,generics.ListAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    serializer_class=likedSerializer

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset =(Like.objects.select_related('user','song','song__album').prefetch_related('song__artist','song__genre','song__album__artists')).order_by('-id')
    #     if user.is_superuser or user.is_staff:
    #         return queryset
    #     return queryset.filter(user=user)

    def set_queryset_call(self):
        return (Like.objects.select_related('user','song','song__album').prefetch_related('song__artist','song__genre','song__album__artists')).order_by('-id')
    

        
class like_edit_views(OwnerStaffSuperuserQuerysetMixin,generics.RetrieveUpdateAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsAuthenticated,IsOwnerAndSuperuserOnly]
    serializer_class=likedSerializer

    def set_queryset_call(self):
        return (Like.objects.select_related('user','song','song__album').prefetch_related('song__artist','song__genre','song__album__artists'))



# demo use to learn the data with optization and manupliation


class demo_song_model(generics.ListAPIView):
    # def get_queryset(self):
    #     queryset = Songs.objects.all()
    #     fil = self.request.query_params.get("fil")
    #     artist = self.request.query_params.get("art")
    #     if fil and artist:
    #         queryset = queryset.filter(artist__artist_name=artist).exclude(genre__genre_name = fil)
    #     return queryset

    queryset = Songs.objects.annotate(artist_count = Count('artist')).only('id','title','artist__artist_bio').prefetch_related(Prefetch('artist',queryset=Artist.objects.all())).order_by('title','-id')
    serializer_class = demo_song_seralizer

class demo_song_edit_model(generics.RetrieveAPIView):
    queryset = Songs.objects.only('id','title','artist').prefetch_related('artist')
    serializer_class = songSerializer_readonly
    lookup_field = "title"

# demo recommandation for music 

class demo_recommantation_history(generics.ListAPIView):
    serializer_class = demo_history_normal_serializer
    queryset = listen_History_Song_play_Playback.objects.values(
    song_pk =F('song__id')
).annotate(total_count=Sum('count'),total_duration = Sum('duration_played'))
    # .annotate(
    # song_id=F('song__id')
