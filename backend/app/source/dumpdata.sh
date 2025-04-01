# 今のデータをjsonファイルでdumpします！
# 実際は日付を必ず入れてコミットするか安全な場所に退避しよう
# python manage.py dumpdata --exclude admin --exclude auth.permission --exclude auth.group --exclude auth-group-permissions --exclude contenttypes --exclude chatgpt.chatsession --exclude chatgpt.chatmessage > dump.json
python manage.py custom_dumpdata --output dump.json

# インポートする時の操作は、readmeを参照
# （「python manage.py loaddata dump.json」だけではエラーになるので）