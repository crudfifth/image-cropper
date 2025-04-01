from django.core.management.base import BaseCommand

from ...sensor import get_access_token
from ...sensor import get_kensyo_access_token
from ...sensor import floor_environment
from ...sensor import area_environment
from ...sensor import area_congestion
from ...sensor import toilet
from ...sensor import congestion_camera


class Command(BaseCommand):
    def handle(self, *args, **options):

        # e.g. python manage.py cmd_sensor --type token
        if(options['type'] == "token"):
            print(get_access_token())

        # e.g. python manage.py cmd_sensor --type kensyo_token
        if(options['type'] == "kensyo_token"):
            print(get_kensyo_access_token())

        # e.g. python manage.py cmd_sensor --type floor_environment --mode single --value 101B001
        # e.g. python manage.py cmd_sensor --type floor_environment --mode all
        if(options['type'] == "floor_environment"):
            if(options['mode'] == "all"):
                floor_environment("all")
            else:
                floor_environment('single', (options['value']))

        # e.g. python manage.py cmd_sensor --type area_environment --mode single --value 101F020004
        # e.g. python manage.py cmd_sensor --type area_environment --mode all
        if(options['type'] == "area_environment"):
            if(options['mode'] == "all"):
                area_environment("all")
            else:
                area_environment('single', (options['value']))

        # e.g. python manage.py cmd_sensor --type area_congestion --mode single --value 101F001004
        # e.g. python manage.py cmd_sensor --type area_congestion --mode all
        if(options['type'] == "area_congestion"):
            if(options['mode'] == "all"):
                area_congestion("all")
            else:
                area_congestion('single', (options['value']))

        # e.g. python manage.py cmd_sensor --type toilet --mode single --value 101F001
        # e.g. python manage.py cmd_sensor --type toilet --mode all
        if(options['type'] == "toilet"):
            if(options['mode'] == "all"):
                toilet("all")
            elif(options['mode'] == "newall"):
                toilet("newall")
            else:
                toilet('single', (options['value']))

        # e.g. python manage.py cmd_sensor --type congestion_camera --mode single --value 0201XP
        # e.g. python manage.py cmd_sensor --type congestion_camera --mode all
        if(options['type'] == "congestion_camera"):
            if(options['mode'] == "all"):
                congestion_camera("all")
            else:
                congestion_camera('single', (options['value']))

    def add_arguments(self, parser):
        parser.add_argument('--type', nargs='?', default='', type=str)
        parser.add_argument('--mode', nargs='?', default='', type=str)
        parser.add_argument('--value', nargs='?', default='', type=str)