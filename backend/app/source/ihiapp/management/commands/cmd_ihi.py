from django.core.management.base import BaseCommand

from ...function_recored import create_record, delete_all_data, update_water_fuel_data, delete_all_data
from ...function_csv import import_csv
from ...function_update_data import update_push_log



class Command(BaseCommand):
    def handle(self, *args, **options):

        # e.g. python manage.py cmd_sensor --type record
        if(options['type'] == "record"):
            print(create_record())
        if(options['type'] == "delete"):
            print(delete_all_data())
        if(options['type'] == "import"):
            import_csv()
        if(options['type'] == "update"):
            update_push_log()
        if(options['type'] == "water_fuel"):
            update_water_fuel_data()
        if(options['type'] == "delete_all_data"):
            delete_all_data()
            


    def add_arguments(self, parser):
        parser.add_argument('--type', nargs='?', default='', type=str)
        parser.add_argument('--mode', nargs='?', default='', type=str)
        parser.add_argument('--value', nargs='?', default='', type=str)