from django.urls import path
from . import views

urlpatterns = [
    # Ruta para la bandeja de entrada (mensajes recibidos)
    path('inbox/', views.inbox, name='inbox'),
    path('', views.index, name='index'),

    # Ruta para enviar un mensaje a un usuario
    path('send_message/', views.send_message, name='send_message'),
    path('send_message/<int:receiver_id>/', views.send_message, name='send_message'),
    # Ruta para ver los detalles de un mensaje
    path('message/detail/<int:message_id>/', views.message_detail, name='message_detail'),

    # Ruta para marcar un mensaje como spam
    path('message/mark_spam/<int:message_id>/', views.mark_as_spam, name='mark_spam'),

    # Ruta para la búsqueda de mensajes (si la necesitas por separado)
    path('search/', views.search_messages, name='search_messages'),
    path('chat/<int:receiver_id>/', views.chat, name='chat'),
]
