from celery import shared_task
import time
from .models import BackgroundJob

@shared_task(bind = True)
def run_heavy_task(self,job_id):
    job = BackgroundJob.objects.get(id=job_id)

    job.status = 'processing'
    job.save()

    # simulate heavy work
    for i in range(5):
        time.sleep(2)

    job.status ='completed'
    job.result ='Task finished successfully'
    job.save()

    return 'Done'


'''
# tasks.py
from celery import shared_task
import time
from .models import demo_task

@shared_task(bind=True, max_retries=3)
def runbackground_task(self, job_id):
    try:
        job = demo_task.objects.get(id=job_id)

        job.status = "processing"
        job.save(update_fields=["status"])

        # 🔴 Simulated failure
        if job.title == "fail":
            raise Exception("Simulated task failure")

        for i in range(1, 11):
            time.sleep(1)
            progress_value = i * 10
            job.progress = progress_value
            job.result = f"Loading {progress_value}%"
            job.save(update_fields=["progress", "result"])

        job.status = "completed"
        job.result = "Task completed"
        job.progress = 100
        job.save(update_fields=["status", "result", "progress"])

        return "done"

    except Exception as exc:
        print(f"Retrying... Attempt {self.request.retries + 1}")

        # Retry after 5 seconds
        raise self.retry(exc=exc, countdown=5)

'''