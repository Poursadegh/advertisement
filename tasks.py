from celery import shared_task
from .models import Advertisement


@shared_task
def update_advertisements_views():
    advertisements = Advertisement.objects.all()
    for advertisement in advertisements:
        advertisement.views += 1
        advertisement.save()
