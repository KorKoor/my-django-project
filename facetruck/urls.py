from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from posts import views
from posts.views import (
    index, post_comments, register, profile, create_post, 
    edit_profile, search, like_post, add_comment, delete_post, inbox
)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),  # Acceso al panel de administración

    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),  # Rutas predefinidas de autenticación (login, logout, etc.)
    path('accounts/register/', register, name='register'),  # Registro de nuevos usuarios

    # Ruta de Logout usando la vista predeterminada de Django
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # Cerrar sesión

    # Rutas de la aplicación principal
    path('', index, name='index'),  # Página principal (feed de publicaciones)
    
    # Perfil de usuario (usamos el ID del perfil para mostrar el perfil de un usuario específico)
    path('profile/<int:user_id>/', profile, name='profile'),  # Perfil de un usuario específico (por ID dinámico)
    
    # Editar perfil del usuario autenticado (no necesita el user_id en la URL)
    path('profile/edit/', edit_profile, name='edit_profile'),  # Editar perfil

    path('create/', create_post, name='create_post'),  # Crear una nueva publicación
    path('search/', views.search, name='search'),  # Buscar publicaciones o usuarios
    
    path('like/<int:post_id>/', like_post, name='like_post'),  # Asegúrate de que esta URL esté definida en tus vistas
    path('add_comment/<int:post_id>/', add_comment, name='add_comment'),  # Lo mismo para los comentarios

    # Ruta para eliminar una publicación
    path('post/delete/<int:post_id>/', delete_post, name='delete_post'),

    # Incluir las rutas de mensajes (esto es modular) 
    path('messages/', include('posts.urls')),  # Incluye las rutas de mensajes en posts/urls.py
    
    # Otras rutas...
    path('help/', views.help_page, name='help_page'),
]

# Configuración de archivos estáticos y de medios
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
