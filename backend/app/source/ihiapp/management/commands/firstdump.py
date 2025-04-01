
from django.core.management.base import BaseCommand
import pickle

class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open('list.txt','wb')
        list_row = {
            'grant_type'    : 'password',              	# authorization_code
            'client_id'     : 'wow_client',			# クライアントID
            'client_secret' : '11111111-2222-3333-4444-555555555555',# クライアントシークレット                   	# 認可コード
            'username'      : 'wow_service',
            'password'      : 'wow_service_2021',
        }
        print(list_row)
        pickle.dump(list_row, f)
        