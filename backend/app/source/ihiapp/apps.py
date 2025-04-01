from config.settings import FRONTEND_URL
from django.apps import AppConfig
from django.core.mail import send_mail
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from .function_create_set_password_message import create_set_password_message
from .constants import SENDER_EMAIL
from .function_send_mail import send_mail_from_service

class IhiappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ihiapp'


    def ready(self):
       """
       This function is called when startup.
       """

       # signalsの処理を有効化するためのimportのため、削除しないこと
       import ihiapp.signals

       from .cron import start
       start()

    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, reset_password_token, *args, **kwargs):
        if reset_password_token is None:
            return
        email_subject = "【IHIダッシュボード運営事務局】 パスワード設定・再設定について"
        url = f"{FRONTEND_URL}/reset-password?token={reset_password_token.key}"
        email_body = create_set_password_message(url)
        send_mail_from_service(email_subject, email_body, [reset_password_token.user.email])