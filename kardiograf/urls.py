from django.contrib import admin
from django.urls import path, include
from . import views
from .views import kardiograf, errorPage, listUsers,mqtt
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('kardiograf', kardiograf.countBerth, name='countBerth'),
    path('rekam-medik', kardiograf.rekamMedik, name='rekamMedik'),
    path('profile', kardiograf.profile, name="profile"),
    path('detail-lead', kardiograf.detailLead, name="detailLead" ),
    path('publish_mqtt/', kardiograf.publish_mqtt, name="publish_mqtt"),
    path('save-ekg-data/', kardiograf.save_ekg_data, name="save_ekg_data"),
    path('view-history/', kardiograf.heart_rate_history, name='viewPerhitunganData'),
    path('delete-perhitungan/<int:pk>/', kardiograf.delete_perhitungan, name='delete_perhitungan'),
    path('ajikk/', kardiograf.ajikk, name="ajikk"),
    path('api/get_heart_rate_data/<int:user_id>/', kardiograf.get_heart_rate_data_by_user_id, name='get_heart_rate_data_by_user_id'),
    path('error', errorPage.needLogin, name="needLogin"),
    path('api/get_all_users/', listUsers.get_all_users, name='get_all_users'),
    path('delete_user/<int:user_id>/', listUsers.delete_user, name='delete_user'),
    path('save_heart_rate/', views.save_heart_rate, name='save_heart_rate'),
    path('mqtt_subscribe/', mqtt.mqtt_subscribe, name='mqtt_subscribe'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)