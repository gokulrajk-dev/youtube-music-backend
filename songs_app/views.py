from datetime import date, timedelta, timezone

from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.models import F, Max, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status  # type: ignore
from rest_framework import filters, generics, pagination, viewsets
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import api_view
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView  # type: ignore

from .filter import *
from .models import *
from .permission import *
from .serializers import *
from user_account_app.permission import *

# User = get_user_model()

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
    authentication_classes=[SessionAuthentication]
    permission_classes=[IsSuperUser]
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

# crud for genre

class genre_views(viewsets.ModelViewSet):
    authentication_classes=[SessionAuthentication]
    permission_classes = [Issuper_user_only_other_readonly]
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

# crud for album

class album_views(viewsets.ModelViewSet):
    authentication_classes=[SessionAuthentication]
    permission_classes=[Issuper_user_only_other_readonly]
    queryset=Album.objects.all().prefetch_related('artists')
    serializer_class=AlbumSerializer

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
     
    def get_serializer_class(self):
        if self.request.method in ['POST','PUT','PATCH']:
            return songsSerializer_writeonly
        return songSerializer_readonly
    
        

class songs_edit_views(generics.RetrieveDestroyAPIView):
    authentication_classes=[SessionAuthentication]
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
    queryset = Songs.objects.all().select_related('album','video_song').prefetch_related('artist','genre')
    serializer_class = video_song_in_songs
    
# crud of video_song

class video_songs_views(generics.ListCreateAPIView):
    authentication_classes=[SessionAuthentication]
    permission_classes=[Issuper_user_only_other_readonly]
    queryset = video_song.objects.all()
    serializer_class = video_songSerialize
    
# crud for playlists
class playlist_views(generics.ListCreateAPIView):
    authentication_classes=[SessionAuthentication]
    permission_classes=[IsAuthenticated,isOwnerorReadOnly]
    serializer_class=playlistSerializer

    def get_queryset(self):
        return (
            Playlist.objects.filter(user=self.request.user).select_related('user').prefetch_related('songs','songs__artist','songs__album','songs__genre','songs__album__artists')
        )

    # def get(self,request):
    #     data = Playlist.objects.all().select_related('user').prefetch_related('songs','songs__artist','songs__album','songs__genre','songs__album__artists')
    #     serializer = playlistSerializer(data,many=True)
    #     return Response(serializer.data,200)

class playlist_edit_views(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[SessionAuthentication]
    permission_classes=[IsAuthenticated,isOwnerorReadOnly]
    queryset =Playlist.objects.all().select_related('user').prefetch_related('songs','songs__artist','songs__album','songs__genre','songs__album__artists')
    serializer_class =playlistSerializer

# crud for listen history
# measure play count , play time , add views to songs over 30 second , sort by day like
# youtube music history manage


class listen_history_views_post(APIView):
    def post(self,request):
        user_id = request.data.get("user_id")
        song_id = request.data.get("songs_id")
        durations = request.data.get("duration")

        if not user_id  or not song_id or not durations :
            return Response({"message":"all field is required"})
        
        user = get_object_or_404(CustomUser,id=user_id)
        song = get_object_or_404(Songs,id = song_id)
        durationss = timedelta(seconds=int(durations))
        dates = timezone.localdate()
        now = timezone.now()
            
        with transaction.atomic():
            history,created= listen_History_Song_play_Playback.objects.get_or_create(
                user=user,
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
                one_minute_ago = timezone.now() - timedelta(minutes=1)

                already_count = listen_History_Song_play_Playback.objects.filter(
                    user=user,
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
        


class listen_history_views(generics.ListAPIView):
    queryset = (
        listen_History_Song_play_Playback.objects
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
    serializer_class=listenhistorySerializer
    


class history_edit_views(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly,IsAuthenticated]
    queryset = (
        listen_History_Song_play_Playback.objects
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
    serializer_class=listenhistorySerializer

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



class like_views(generics.ListAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsOwnerAndSuperuserOnly]
    serializer_class=likedSerializer

    def get_queryset(self):
        user = self.request.user
        queryset =(Like.objects.select_related('user','song','song__album').prefetch_related('song__artist','song__genre','song__album__artists')).order_by('-id')
        if user.is_superuser or user.is_staff:
            return queryset
        return queryset.filter(user=user)
    
        
class like_edit_views(OwnerStaffSuperuserQuerysetMixin,generics.RetrieveUpdateAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes=[IsAuthenticated,IsOwnerAndSuperuserOnly]
    serializer_class=likedSerializer

    def set_queryset_call(self):
        return (Like.objects.select_related('user','song','song__album').prefetch_related('song__artist','song__genre','song__album__artists'))

