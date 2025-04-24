from django_cron import CronJobBase, Schedule
from nft.models import Item
from datetime import datetime

class CancelExpiredListingsCronJob(CronJobBase):
    RUN_EVERY_MINS = 5  # 5분마다 실행

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'nft.cancel_expired_listings'  # 고유 코드

    def do(self):
        now = datetime.now()
        expired_items = Item.objects.filter(is_listed=True, listing_duration__lte=now)

        for item in expired_items:
            item.is_listed = False
            item.save()
