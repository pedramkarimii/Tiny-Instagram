from django.core.management.base import BaseCommand
from account.models import OptCode
from datetime import datetime, timedelta
import pytz


class Command(BaseCommand):
    help = "Delete all expired OTP code"

    def handle(self, *args, **options):
        expired_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
        OptCode.objects.filter(created__lt=expired_time).delete()
        self.stdout.write("Deleted all expired OTP code.")
