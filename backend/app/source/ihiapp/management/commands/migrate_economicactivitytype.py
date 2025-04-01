from django.core.management.base import BaseCommand
from django.db import transaction
from ihiapp.models import EconomicActivityType


class Command(BaseCommand):
    help = 'Migrates company from user field to company field in MonthlyCostTarget in batches'

    def handle(self, *args, **kwargs):
        batch_size = 1000

        with transaction.atomic():
            for activity_type in EconomicActivityType.objects.iterator(chunk_size=batch_size):
                if activity_type.user_id:
                    activity_type.company = activity_type.user_id.company_id
                    activity_type.save()

        self.stdout.write(self.style.SUCCESS('Successfully migrated economic activty type data'))
