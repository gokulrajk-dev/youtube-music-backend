from django.contrib import admin

from .models import *

# Register your models here.


admin.site.register(Songs)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Playlist)
admin.site.register(listen_History_Song_play_Playback)
admin.site.register(Queue)
admin.site.register(Genre)
admin.site.register(Like)
admin.site.register(Block_songs)
