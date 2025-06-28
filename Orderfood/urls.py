from django.urls import path
from . import views

urlpatterns = [
    # Homepage - List of Canteens
    path('', views.canteen, name='order'),

    # Static paths (must be defined before dynamic slugs)
    path('my-orders/', views.view_orders, name='view_order'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),  # Optional: add this if cancel support is added

    # Slug-based dynamic routes (placed at the end to avoid catching static paths)
    path('<slug:slug>/add-to-cart/<int:item_id>/', views.addtocart, name='add_to_cart'),
    path('<slug:slug>/remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('<slug:slug>/', views.menu_page, name='menu_page'),
    path('track-order/<int:order_id>/', views.track_order, name='track-order'),
    path('<path>/', views.errorpage, name='error'),

]
