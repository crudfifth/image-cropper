"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from django.urls import include
# from ihiapp.urls import router as ihiapp_router
# from ihiapp.urls import urlpatterns as ihiapp_urlpatterns

from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer

from rest_framework.documentation import include_docs_urls

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import CustomTokenObtainPairView

schema_view = get_schema_view(title='Addressess API',
                              url='http://localhost:18899/api/',
                              renderer_classes=[JSONOpenAPIRenderer]
                              )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('ihiapp.urls')),
    path('api/v2/', include('ihiapp.v2.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'), 
]
