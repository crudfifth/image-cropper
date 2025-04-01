from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import exceptions
from ihiapp.models import User
from axes.models import AccessAttempt

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # ユーザーが存在しない場合は、親のpostメソッドをそのまま呼び出す
            return super().post(request, *args, **kwargs)

        if user.is_locked:
            raise exceptions.PermissionDenied(detail="アカウントがロックされています。")

        response = super().post(request, *args, **kwargs)

        # ログイン成功時には、ログイン失敗回数をリセットする
        # AXESにおいてAXES_RESET_ON_SUCCESSという設定項目があるが、JWT認証を使うと機能しない (おそらくuser_logged_inシグナルが飛ばないため)
        if response.status_code == 200:
            AccessAttempt.objects.filter(username=user.email).delete()

        return response
