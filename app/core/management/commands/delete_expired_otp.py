from django.core.management.base import BaseCommand
from app.account.models import OptCode
from datetime import datetime, timedelta
import pytz


class Command(BaseCommand):
    """
    Defines a management command to delete all expired OTP codes.
    Deletes OTP codes that were created more than 2 minutes ago.
    """
    help = "Delete all expired OTP code"

    def handle(self, *args, **options):
        expired_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
        OptCode.objects.filter(created__lt=expired_time).delete()
        self.stdout.write("Deleted all expired OTP code.")
