from django.db import models
from django.conf import settings  # Para usar AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

# Modelo de usuario personalizado que extiende AbstractUser
class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return self.username


# Modelo de perfil de usuario asociado al CustomUser
class UserProfile(models.Model):
    """
    Modelo de perfil de usuario asociado al CustomUser.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    school_name = models.CharField(max_length=100, blank=True, null=True)
    highschool_name = models.CharField(max_length=100, blank=True, null=True)
    university_name = models.CharField(max_length=100, blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    work_experience = models.TextField(blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_picture = models.ImageField(upload_to='cover_pics/', blank=True, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

    @property
    def age(self):
        """
        Calcula la edad basada en la fecha de nacimiento.
        """
        if self.date_of_birth:
            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return None

    @property
    def has_social_links(self):
        """
        Verifica si el usuario tiene enlaces sociales configurados.
        """
        return bool(self.social_links)


# Modelo para las publicaciones de usuarios
class Post(models.Model):
    """
    Modelo para las publicaciones de usuarios.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts'
    )
    content = models.TextField()
    image = models.ImageField(upload_to='posts_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True
    )

    def __str__(self):
        return f'{self.user.username}: {self.content[:30]}'

    class Meta:
        ordering = ['-created_at']

    @property
    def like_count(self):
        """
        Devuelve la cantidad de "me gusta".
        """
        return self.likes.count()

    @property
    def comment_count(self):
        """
        Devuelve la cantidad de comentarios.
        """
        return self.comments.count()


# Modelo para los comentarios en publicaciones
class Comment(models.Model):
    """
    Modelo para los comentarios en publicaciones.
    """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.content[:20]}'

    class Meta:
        ordering = ['created_at']


# Modelo para las conversaciones de mensajes entre usuarios
class Conversation(models.Model):
    """
    Modelo para las conversaciones entre dos o más usuarios.
    """
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversación entre {', '.join([user.username for user in self.users.all()])}"

    @property
    def message_count(self):
        """
        Devuelve la cantidad de mensajes en la conversación.
        """
        return self.messages.count()


# Modelo para los mensajes entre usuarios
from django.db import models
from django.conf import settings
from django.utils import timezone

from django.db import models
from django.conf import settings

from django.conf import settings
from django.db import models

from django.db import models
from django.conf import settings

from django.utils import timezone
from django.db import models
from django.conf import settings

class Message(models.Model):
    """
    Modelo para los mensajes entre usuarios.
    Cada mensaje está asociado a una conversación entre dos usuarios, y puede contener texto y archivos adjuntos.
    """
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages', null=True, blank=True)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField(blank=True, null=True)  # Permitimos que el contenido sea vacío para mensajes con solo archivos
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de actualización automática
    is_read = models.BooleanField(default=False)  # Marcar si el mensaje ha sido leído
    is_spam = models.BooleanField(default=False)  # Marcar si el mensaje es spam
    
    # Adjuntos (imagenes, documentos, etc.)
    attachment = models.FileField(upload_to='messages/attachments/', null=True, blank=True)
    
    # Indicador de tipo de mensaje (texto, imagen, archivo, etc.)
    message_type = models.CharField(
        max_length=50,
        choices=[('text', 'Texto'), ('image', 'Imagen'), ('file', 'Archivo')],
        default='text'
    )
    
    class Meta:
        # Ordenar los mensajes por fecha de creación (más recientes primero)
        indexes = [
            models.Index(fields=['sender', 'receiver', 'created_at']),
        ]
        ordering = ['-created_at']  # Los mensajes se ordenan por fecha de creación descendente

    def __str__(self):
        # Muestra los primeros 20 caracteres del contenido como resumen
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}..."  

    # Métodos útiles
    def mark_as_read(self):
        """Marca el mensaje como leído"""
        self.is_read = True
        self.save()

    def mark_as_spam(self):
        """Marca el mensaje como spam"""
        self.is_spam = True
        self.save()

    def get_attachment_url(self):
        """Devuelve la URL del archivo adjunto si existe"""
        return self.attachment.url if self.attachment else None

    @classmethod
    def unread_messages_count(cls, user):
        """Devuelve la cantidad de mensajes no leídos para un usuario"""
        return cls.objects.filter(receiver=user, is_read=False).count()

    @classmethod
    def spam_messages(cls, user):
        """Devuelve todos los mensajes marcados como spam para un usuario"""
        return cls.objects.filter(receiver=user, is_spam=True)
# Señales para crear y guardar perfiles automáticamente al crear usuarios
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea un perfil de usuario automáticamente al crear un CustomUser.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda automáticamente el perfil de usuario al guardar un CustomUser.
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
