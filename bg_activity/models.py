from django.db import models

class BackgroundJob(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default="pending")
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def __str__(self):
        return self.title