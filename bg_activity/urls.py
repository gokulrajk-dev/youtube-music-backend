from django.urls import path
from .views import CreateJobView, JobStatusView

urlpatterns = [
    path("create/", CreateJobView.as_view()),
    path("status/<int:job_id>/", JobStatusView.as_view()),
]
