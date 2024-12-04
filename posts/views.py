from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import CustomUser, Post, UserProfile, Comment, Message
from .forms import PostForm, UserProfileForm, CommentForm, CustomUserCreationForm, MessageForm
from django.contrib.auth import logout
from django.conf import settings


# Vista para registrar usuarios
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save()

            # Enviar correo de bienvenida
            send_mail(
                'Bienvenido a FaceTruck',
                f'Hola {user.username},\n\nGracias por registrarte en nuestra plataforma. Tu cuenta ha sido creada correctamente.\n\n¡Disfruta de nuestra aplicación!',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            messages.success(request, "Te has registrado exitosamente. ¡Bienvenido!")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# Vista para mostrar el perfil del usuario
@login_required
def profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    user_posts = Post.objects.filter(user=user).select_related('user').order_by('-created_at')
    is_owner = user == request.user
    no_posts_message = "Este usuario no ha publicado aún." if not user_posts.exists() else None

    return render(request, 'posts/profile.html', {
        'user': user,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'is_owner': is_owner,
        'no_posts_message': no_posts_message
    })


# Vista para agregar comentarios a una publicación
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comentario agregado correctamente.")
            return redirect('profile', user_id=request.user.id)
    else:
        form = CommentForm()
    return redirect('index')


# Vista para manejar "me gusta"
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.info(request, "Quitaste tu 'Me gusta'.")
    else:
        post.likes.add(request.user)
        messages.success(request, "¡Te gustó esta publicación!")
    return redirect('index')


# Vista para editar el perfil del usuario actual
@login_required
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('profile', user_id=request.user.id)
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'posts/edit_profile.html', {'form': form})


# Vista para crear una publicación
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Publicación creada exitosamente.")
            return redirect('index')
    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


# Vista para eliminar una publicación
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
        messages.success(request, "Publicación eliminada exitosamente.")
    else:
        messages.error(request, "No tienes permiso para eliminar esta publicación.")
    
    return redirect('index')


# Vista para la bandeja de entrada (mensajes recibidos)
@login_required
def inbox(request):
    # Obtener los mensajes recibidos por el usuario
    messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'posts/inbox.html', {'messages': messages})


# Vista para enviar un mensaje
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Message

@login_required
def send_message(request, receiver_id=None):
    receiver = None
    receiver_username = request.GET.get('receiver_username', '')  # Recuperar el nombre de usuario si existe

    # Buscar el receptor si se pasa el `receiver_id` como argumento
    if receiver_id:
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            receiver = None

    # Si se envió un mensaje, procesarlo
    if request.method == 'POST':
        if receiver:
            # Si hay un receptor, guardar el mensaje
            content = request.POST.get('content').strip()
            if content:
                Message.objects.create(sender=request.user, receiver=receiver, content=content)
                messages.success(request, "Mensaje enviado con éxito.")
                return redirect('send_message', receiver_id=receiver.id)
            else:
                messages.error(request, "El mensaje no puede estar vacío.")
                return redirect('send_message', receiver_id=receiver.id)

        else:
            # Si se está buscando un usuario por nombre
            receiver_username = request.POST.get('receiver_username')
            try:
                receiver = CustomUser.objects.get(username=receiver_username)
            except CustomUser.DoesNotExist:
                receiver = None

            if receiver:
                # Redirigir al formulario con el receptor seleccionado
                return redirect('send_message', receiver_id=receiver.id)
            else:
                # Mostrar error si el usuario no existe
                messages.error(request, f"El usuario '{receiver_username}' no se encontró.")
                return redirect('send_message')

    # Obtener todos los usuarios disponibles para buscar, excluyendo al usuario actual
    users = CustomUser.objects.exclude(id=request.user.id)  # Excluir el usuario actual de los resultados

    # Obtener los mensajes previos con el receptor seleccionado (si existe)
    messages_previos = []
    if receiver:
        messages_previos = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=request.user))
        ).order_by('created_at')

    return render(request, 'posts/send_message.html', {
        'receiver': receiver,
        'users': users,
        'receiver_username': receiver_username,
        'messages': messages_previos,  # Enviar los mensajes previos a la plantilla
    })
# Vista para ver los detalles de un mensaje
@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    return render(request, 'posts/message_details.html', {'message': message})


# Vista para la búsqueda de mensajes y usuarios
def search(request):
    query = request.GET.get('q', '')
    
    if query:
        # Filtrar publicaciones que contengan la palabra clave en el contenido
        posts = Post.objects.filter(Q(content__icontains=query))
        # Filtrar usuarios cuyo nombre de usuario contenga la palabra clave
        users = CustomUser.objects.filter(Q(username__icontains=query))
    else:
        posts = Post.objects.none()
        users = CustomUser.objects.none()

    return render(request, 'posts/search_results.html', {
        'posts': posts,
        'users': users,
        'query': query
    })


@login_required
def search_messages(request):
    query = request.GET.get('q', '')  # Obtener el parámetro de búsqueda
    if query:
        # Filtrar mensajes que contienen la búsqueda en el contenido
        messages = Message.objects.filter(content__icontains=query)
        # Filtrar usuarios que contienen la búsqueda en el nombre de usuario
        users = CustomUser.objects.filter(username__icontains=query)
    else:
        # Si no hay consulta, no mostrar resultados
        messages = Message.objects.none()
        users = CustomUser.objects.none()

    # Pasar los resultados a la plantilla
    return render(request, 'posts/index.html', {
        'messages': messages,
        'users': users,
    })


# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada exitosamente.")
    return redirect('login')


from django.contrib.auth.decorators import login_required
from .models import Post, Message
from django.db.models import Q
from django.contrib.auth import get_user_model

# Usamos el modelo de usuario personalizado
CustomUser = get_user_model()

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, Message, CustomUser

@login_required
def index(request):
    # Obtener todas las publicaciones sin paginación
    posts = Post.objects.all().select_related('user').order_by('-created_at')

    # Obtener los mensajes no leídos para la barra lateral
    unread_messages = Message.objects.filter(
        receiver=request.user, 
        is_read=False
    ).order_by('created_at')

    # Obtener los mensajes marcados como spam
    spam_messages = Message.objects.filter(receiver=request.user, is_spam=True).order_by('-created_at')

    # Verificar si hay algún receptor (último mensaje no leído)
    if unread_messages.exists():
        receiver_id = unread_messages.first().sender.id
    else:
        receiver_id = None  # Si no hay mensajes no leídos, no asignamos receptor

    # Manejo de búsqueda
    query = request.GET.get('q', '')
    if query:
        messages = Message.objects.filter(
            Q(content__icontains=query) | 
            Q(sender__username__icontains=query) | 
            Q(receiver__username__icontains=query)
        ).order_by('-created_at')

        users = CustomUser.objects.filter(username__icontains=query)
    else:
        messages = []
        users = []

    # Obtener los chats previos
    chats = []
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('created_at')

    # Agrupar los mensajes por usuario
    users_in_conversations = set()
    for message in messages:
        other_user = message.sender if message.receiver == request.user else message.receiver
        if other_user != request.user:
            if other_user not in users_in_conversations:
                users_in_conversations.add(other_user)
                last_message = Message.objects.filter(
                    (Q(sender=other_user) & Q(receiver=request.user)) | 
                    (Q(sender=request.user) & Q(receiver=other_user))
                ).order_by('-created_at').first()
                chats.append({
                    'other_user': other_user,
                    'last_message': last_message,
                    'unread': last_message.receiver == request.user and not last_message.is_read
                })

    # Ordenar los chats por fecha del último mensaje
    chats = sorted(chats, key=lambda x: x['last_message'].created_at, reverse=True)

    # Pasar los datos a la plantilla
    return render(request, 'posts/index.html', {
        'posts': posts,
        'unread_messages': unread_messages,
        'spam_messages': spam_messages,
        'receiver_id': receiver_id,
        'messages': messages,
        'users': users,
        'chats': chats,  # Chats previos
    })

# Vista para los comentarios de una publicación
def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'posts/post_comments.html', {'post': post, 'comments': comments})


# Vista para la página de ayuda
def help_page(request):
    return render(request, 'posts/help_page.html')


# Vista para marcar un mensaje como leído
from django.shortcuts import get_object_or_404, redirect
from .models import Message

def mark_as_read(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Marcar el mensaje como leído
    if not message.is_read:
        message.is_read = True
        message.save()

    # Redirigir de nuevo a la página de detalles del mensaje
    return redirect('message_detail', message_id=message.id)

# Vista para marcar un mensaje como spam
from django.shortcuts import render, redirect
from .models import Message

def mark_as_spam(request, message_id):
    message = Message.objects.get(id=message_id)
    
    # Lógica para marcar el mensaje como spam
    message.is_spam = True
    message.save()

    # Redirigir con el mensaje de confirmación
    return render(request, 'message/mark_as_spam.html', {
        'message': message,
        'marked_as_spam': True
    })

@login_required
def message_send(request):
    return render(request, 'posts/message_send.html')

from django.shortcuts import render
from .models import Message, CustomUser

from django.http import JsonResponse
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Q
from .models import Message
from .models import CustomUser  # Asegúrate de importar CustomUser si no lo has hecho

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Message, CustomUser
from django.db.models import Q
import json

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Message
from django.db.models import Q
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Message, CustomUser
from django.db.models import Q
import json

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Message
from .models import CustomUser

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message, CustomUser

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Message, CustomUser

@login_required
def chat(request, receiver_id):
    # Obtener el receptor (usuario con el que se va a chatear)
    try:
        receiver = CustomUser.objects.get(id=receiver_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

    # Consultar los mensajes entre el usuario actual y el receptor, ordenados de más recientes a más antiguos
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('-created_at')[:50]  # Los más recientes primero y limitados a los últimos 50 mensajes

    # Marcar mensajes no leídos como leídos
    Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')  # Obtiene la imagen enviada

        if content.strip():  # Solo procesamos si el contenido no está vacío
            # Crear el mensaje
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                message_type='text',  # El tipo de mensaje es texto
            )

            # Si hay una imagen adjunta, la procesamos
            if image:
                message.attachment = image
                message.message_type = 'image'  # Actualizamos el tipo de mensaje a 'image'
                message.save()

            # Devolver los mensajes actualizados sin necesidad de recargar la página
            return render(request, 'posts/chat.html', {
                'receiver': receiver,
                'messages': Message.objects.filter(
                    (Q(sender=request.user) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=request.user))
                ).order_by('-created_at')[:50],  # Volver a mostrar los últimos mensajes
            })

    # Si la petición no es POST, simplemente renderizar la página con los mensajes previos
    return render(request, 'posts/chat.html', {
        'receiver': receiver,
        'messages': messages,
    })
