import jwt
from config.settings import SECRET_KEY
from jwt.exceptions import ExpiredSignatureError
from django.http import JsonResponse

from .models import User


class DenyDemoUserMiddleware():

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # デモユーザの書き込み系操作には403を返す

        # 書き込み以外の操作を許可する
        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            response = self.get_response(request)
            return response

        # アクセストークンのリフレッシュだけは特別に許可する (こうしないとフロントエンド側のAPIコールがループになってしまうため)
        if request.path == "/api/v1/token/refresh/":
            response = self.get_response(request)
            return response

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # DRFのミドルウェアの中ではrequest.userにより認証ユーザを取得できない(AnonymousUserとなる)ため、
            # JWTのペイロードからユーザを取得する
            JWT = auth_header.split(" ")[1]
            try: 
                payload = jwt.decode(jwt=JWT, key=SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=payload["user_id"])

                if user.is_authenticated and user.is_demo:
                    return JsonResponse({
                        "detail": "デモユーザによる書き込みは禁止されています。",
                        "error_type": "demo_user_restricted"
                    }, status=403)
                response = self.get_response(request)
                return response
            except ExpiredSignatureError:
                return JsonResponse({
                    "detail": "トークンの有効期限が切れています。",
                    "error_type": "token_expired"
                }, status=401)
            except Exception as e:
                return JsonResponse({
                    "detail": str(e),
                }, status=401)

        response = self.get_response(request) 
        return response
