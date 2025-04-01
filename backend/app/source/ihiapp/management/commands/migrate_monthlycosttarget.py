from django.core.management.base import BaseCommand
from django.db import transaction
from ihiapp.models import MonthlyCostTarget


class Command(BaseCommand):
    help = 'Migrates company from user field to company field in MonthlyCostTarget in batches'

    def handle(self, *args, **kwargs):
        batch_size = 1000

        with transaction.atomic():
            for target in MonthlyCostTarget.objects.iterator(chunk_size=batch_size):
                if target.user_id:
                    target.company = target.user_id.company_id
                    target.save()

        self.stdout.write(self.style.SUCCESS('Successfully migrated company data'))
