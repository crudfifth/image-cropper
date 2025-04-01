from django.urls import include, path, re_path
from ihiapp.views import (DataStructureListView, EntityDestroyView,
                          EntityListCreateView,
                          UserEntityPermissionDestroyView,
                          UserEntityPermissionListCreateView)
from rest_framework import routers

from .views import (ChangePasswordView, CompanyViewSet, CurrentUserView,
                    DemoAccountAuthView, IsCompanyAdminView,
                    NotificationDetailView, NotificationListCreateView,
                    PasswordResetConfirmView, PasswordResetRequestView,
                    UpdateDailyRevenueView, UserActivationViewSet, UserViewSet, ActivateUserView, UserByActivationTokenView,
                    create_admin_user, create_user, delete_data)

router_users = routers.DefaultRouter(trailing_slash=False)
router_activate = routers.DefaultRouter(trailing_slash=False)

router_users.register(r"", UserViewSet, basename="User")
router_activate.register(r"", UserActivationViewSet, basename="UserActivation")

urlpatterns = [
    path("user/", CurrentUserView.as_view(), name="CurrentUser"),
    path("users/", include(router_users.urls)),
    path("users/activate/", include(router_activate.urls)),
    path("activate-user/", ActivateUserView.as_view(), name="ActivateUser"),
    path("user-by-activation-token/", UserByActivationTokenView.as_view(), name="UserByActivationToken"),
    path('notifications/', NotificationListCreateView.as_view(), name='NotificationListCreateView'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='NotificationDetailView'),
    path('user/daily_revenue/', UpdateDailyRevenueView.as_view(), name='UpdateDailyRevenue'),
    path('user/change_password/', ChangePasswordView.as_view(), name='ChangePassword'),
    # create_userにて、company_idを受け取るため、re_pathを使用
    re_path(r'^create_user/(?P<company_id>[0-9a-f-]+)/$', create_user, name='create_user'),
    re_path(r'^create_admin_user/(?P<company_id>[0-9a-f-]+)/$', create_admin_user, name='create_admin_user'),
    re_path(r'^delete_data/(?P<company_id>[0-9a-f-]+)/$', delete_data, name='delete_data'),
    path('user/reset_password_request/', PasswordResetRequestView.as_view(), name="set_password_request"),
    path('user/reset_password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="reset_password"),
    path("companies/<uuid:pk>/", CompanyViewSet.as_view({"patch": "partial_update", "get": "retrieve"}), name="CompanyViewSet"),
    path("companies/<uuid:pk>/is_admin/", IsCompanyAdminView.as_view(), name="IsCompanyAdminView"),
    path("companies/<uuid:company_id>/entities/", EntityListCreateView.as_view(), name="EntityListCreateView"),
    path("companies/<uuid:company_id>/entities/<uuid:entity_id>/", EntityDestroyView.as_view(), name="EntityDestroyView"),
    path("companies/<uuid:company_id>/data_structures/", DataStructureListView.as_view(), name="DataStructureListView"),
    path("companies/<uuid:company_id>/user_entity_permissions/", UserEntityPermissionListCreateView.as_view(), name="UserEntityPermissionListCreateView"),
    path("companies/<uuid:company_id>/user_entity_permissions/<uuid:pk>/", UserEntityPermissionDestroyView.as_view(), name="UserEntityPermissionDestroyView"),
    path("companies/", CompanyViewSet.as_view({"get": "list"}), name="CompanyViewSet"),
    path("demo_user_token/", DemoAccountAuthView.as_view(), name="DemoAccountAuthView"),
]
