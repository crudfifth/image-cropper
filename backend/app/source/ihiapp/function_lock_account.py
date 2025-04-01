from users.models import User
import datetime

def search_and_lock_accounts():
    # ロック対象のユーザーを取得
    users = User.objects.filter(is_demo=False, last_login__lte=datetime.datetime.now() - datetime.timedelta(days=90))
    # ロック対象のユーザーがいなければ、処理を終了
    if not users:
        return

    # ロック対象のユーザーをロック
    for user in users:
        user.is_locked = True
        user.save()