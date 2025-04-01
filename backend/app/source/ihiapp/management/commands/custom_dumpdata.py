import json

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.management.commands.dumpdata import Command as DumpDataCommand

class Command(DumpDataCommand):
    help = 'Custom dumpdata command that dumps and then encrypts pushlog_api_keys'

    def handle(self, *args, **options):
        # 一旦dumpdataコマンドのデフォルトの動作を呼び出す
        output_file = options.get('output')
        super().handle(*args, **options)

        # 暗号化処理
        self.encrypt_pushlog_api_key(output_file)

    def encrypt_pushlog_api_key(self, output_file):
        # 暗号化オブジェクトを初期化
        cipher = Fernet(settings.ENCRYPTION_KEY)

        with open(output_file, 'r') as f:
            data = json.load(f)

        for item in data:
            # PushLogApiモデルのエントリーであることを確認
            if item['model'] == 'ihiapp.pushlogapi':
                # keyが存在すれば暗号化
                key = item['fields']['key']
                if key:
                    encrypted_key = cipher.encrypt(key.encode()).decode()
                    item['fields']['key'] = encrypted_key

        # 暗号化されたデータを同じファイルに上書き
        with open(output_file, 'w') as f:
            json.dump(data, f)

        self.stdout.write(self.style.SUCCESS(f'dumped data saved to {output_file}'))
