from django.urls import path
from . import views

urlpatterns = [
    path('',views.CreateRoom,name='create-room'),
    
    path('create-image/<str:username>',views.createImage,name='create-image'),
    path('create-video/<str:username>',views.createVideo,name='create-video'),
    path('create-audio/<str:username>',views.createAudio,name='create-audio'),
    path('delete-message/<str:pk>',views.deleteMessage,name='delete-message'),
    path('set-read-all-message/<str:room_name>/<str:other_username>',views.setReadAllMessage,name='set-read-all-message'),
    path('usermessaged/<str:username>/',views.getAllMessaged_user,name='all-messaged-user'),
    path('room/<str:room_name>/',views.messageView,name='room'),
    path('allnotification/<str:username>/',views.NotificationView,name='all-notification'),
    path('notif-count/<str:username>/',views.notifCount,name='notif-count'),
    path('setread-notif/<str:pk>/',views.setReadNotif,name='setread-notif'),


]