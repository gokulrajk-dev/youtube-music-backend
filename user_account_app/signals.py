from django.db.models.signals import *
from  django.dispatch import receiver
from guardian.shortcuts import *
from songs_app.models import*


@receiver(post_save,sender=Playlist)
def assign_album_permission(sender,instance,created,**kwergs):
    if created:
        assign_perm('view_playlist',instance.user,instance)
        assign_perm('change_playlist',instance.user,instance)
        assign_perm('delete_playlist',instance.user,instance)