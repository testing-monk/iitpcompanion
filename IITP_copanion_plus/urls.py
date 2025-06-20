from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from IITP_copanion_plus import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('assignment/', views.Assignment, name='Assignment'),
    path('order/', views.canteen, name='order'),
    path('search/', views.search, name='search'),
    path('tracker/', views.tracker, name='tracker'),
    path('contact-us/', views.contact_view, name='contact'),
    path('test/', views.test, name='test'),
    path('progress/', views.progress, name='progress'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('feedback/', views.feedback, name='feedback'),
    path('maps/', views.maps, name='maps'),
    path('student_clubs/', views.student_clubs, name='student_clubs'),
    path('clubs/<slug:slug>/', views.club_detail, name='club_detail'),
    path('events/', views.events, name='events'),
    path('events/save/', views.save_event, name='save_event'),
    path('events/api/', views.get_events, name='get_events'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('order/<slug>/', views.menu_page, name='menu_page'),
    path('order/<slug:slug>/add-to-cart/<int:item_id>/', views.addtocart, name='add_to_cart'),
    path('order/<slug:slug>/remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('about/', views.about_us, name='about'),


]

# Static and media files (for development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
