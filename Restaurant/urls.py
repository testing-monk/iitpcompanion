from django.urls import path
from . import views

urlpatterns = [
    path('', views.owner_dashboard, name='owner_dashboard'),
    path("auth/register/", views.register_owner, name="register_owner"),
    path("auth/login/", views.login_owner, name="login_owner"),
    path("auth/logout/", views.logout_owner, name="logout_owner"),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('menu/add/', views.add_menu_item, name='add_menu_item'),
    path("menu/<slug:slug>/delete/", views.delete_menu_item, name="delete_menu_item"),
    path('menu/<int:item_id>/update/', views.update_menu_item, name='update_menu_item'),
    path('dashboard/profile/', views.owner_profile, name='owner_profile'),
    path('dashboard/profile/edit/', views.edit_owner_profile, name='edit_owner_profile'),
    path('dashboard/profile/change-password/', views.owner_change_password, name='owner_change_password'),
    path("order/<int:order_id>/update-status/", views.update_order_status, name="update_order_status"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),

]
