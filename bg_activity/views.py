from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BackgroundJob
from .tasks import run_heavy_task

# Create your views here.
class CreateJobView(APIView):
    def post(self,request):
        title = request.data.get("title")

        job = BackgroundJob.objects.create(title=title)

        run_heavy_task.delay(job.id)

        return Response({
            "message":"job started",
            "job_id":job.id
        })
    
class JobStatusView(APIView):
    def get(self, request, job_id):
        job = BackgroundJob.objects.get(id=job_id)

        return Response({
            "title": job.title,
            "status": job.status,
            "result": job.result
        })
    