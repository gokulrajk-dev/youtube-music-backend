from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('album',album_views)


urlpatterns=[
    # crud of artist
    path('artist_views/',artist_views.as_view({'get':'list','post':'create'}),name='artist'),
    path('artist_views/<int:pk>/',artist_views.as_view({'get':'retrieve','put': 'update', 'delete': 'destroy'}),name='artist'),
    # crud of genre
    path('genre_views/',genre_views.as_view({'get':'list','post':'create'}),name='genre'),
    path('genre_views/<int:pk>/',genre_views.as_view({'get':'retrieve','put': 'update', 'delete': 'destroy'}),name='genre'),
    # crud of album
    path('album_views/',album_views.as_view({'get':'list','post':'create'}),name='genre'),
    path('album_views/<int:pk>/',album_views.as_view({'get':'retrieve','put': 'update', 'delete': 'destroy'}),name='genre'),
    # proper use of modernviweset
    path("", include(router.urls)),
    #crud of songs
    # path('songs_views/',songs_views.as_view(),name='genre'),
    # path('songs_create_views/',songs_create_views.as_view()),
    path('Song_views/',Song_views.as_view({'get':'list','post':'create'})),
    path('Song_demo_edit_views/<int:pk>/',Song_views.as_view({'get':'retrieve','put':'update','delete':'destroy'})),
    path('songs_edit_views/<int:pk>/',songs_edit_views.as_view(),name='genre'),
    path('songs_edit_update_views/<int:pk>/',songs_edit_update_views.as_view()),
    path('songs_for_playlist_views/',songs_for_playlist_views.as_view(),name='song for playlist'),
    # crud of playlist
    path('playlist_views/',playlist_views.as_view(),name='playlist views'),
    path('playlist_edit_views/<int:pk>/',playlist_edit_views.as_view(),name='playlist edit views'),
    # crud of listen history
    path('listen_history_views_post/',listen_history_views_post.as_view(),name='listen history post views'),
    path('listen_history_views/',listen_history_views.as_view(),name='listen history views'),
    path('history_edit_views/<int:pk>/',history_edit_views.as_view(),name='listen history edit views'),
    # path('listen_full_history/',listen_full_history.as_view(),name='listen history edit views'),
    # crud of queue
    path('queue_views/',queue_views.as_view()),
    path('queue_edit_views/',queue_edit_views.as_view()),
    # crud of like
    path('like__views_post/',like__views_post.as_view()),
    path('like_and_unlike_views/',like_and_unlike_views.as_view()),
    path('like_views/',like_views.as_view()),
    path('like_edit_views/<int:pk>/',like_edit_views.as_view()),



    # demo urls for test the video_songs
    path('video_songs_views/',video_songs_views.as_view()),
    path('song_in_video_song_views/',song_in_video_song_views.as_view()),
]
