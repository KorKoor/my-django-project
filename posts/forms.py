from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Post, UserProfile, Comment
import json
from django.core.exceptions import ValidationError

# Validador personalizado para enlaces sociales
def validate_social_links(value):
    """
    Valida que el campo social_links sea un objeto JSON válido.
    """
    if not value or not value.strip():
        return {}  # Retorna un diccionario vacío si el campo está vacío
    try:
        data = json.loads(value)
        if not isinstance(data, dict):
            raise ValidationError("El formato debe ser un objeto JSON. Ejemplo: {'Facebook': 'https://facebook.com'}")
        # Valida que cada clave sea una cadena de texto no vacía y que el valor sea una URL válida
        for key, val in data.items():
            if not isinstance(key, str) or not isinstance(val, str) or not val.startswith("http"):
                raise ValidationError(f"El enlace de '{key}' no es válido. Asegúrate de usar una URL válida.")
        return data
    except json.JSONDecodeError:
        raise ValidationError("Formato JSON inválido. Ejemplo: {'Facebook': 'https://facebook.com'}")

# Formulario para editar el perfil del usuario
class UserProfileForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario.
    """
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'bio', 'date_of_birth', 'hobbies', 'location', 'school_name',
            'highschool_name', 'university_name', 'work_experience', 'social_links',
            'profile_picture', 'cover_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Describe algo sobre ti', 'class': 'form-control'}),
            'hobbies': forms.TextInput(attrs={'placeholder': 'Hobbies', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'placeholder': 'Ubicación actual', 'class': 'form-control'}),
            'school_name': forms.TextInput(attrs={'placeholder': 'Nombre de tu escuela', 'class': 'form-control'}),
            'highschool_name': forms.TextInput(attrs={'placeholder': 'Nombre de tu secundaria', 'class': 'form-control'}),
            'university_name': forms.TextInput(attrs={'placeholder': 'Nombre de tu universidad', 'class': 'form-control'}),
            'work_experience': forms.Textarea(attrs={'placeholder': 'Describe tu experiencia laboral', 'class': 'form-control'}),
            'social_links': forms.Textarea(attrs={
                'placeholder': 'Enlaces sociales en formato JSON. Ejemplo: {"Facebook": "https://facebook.com"}',
                'class': 'form-control'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'cover_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_social_links(self):
        """
        Valida y normaliza el campo social_links.
        """
        social_links = self.cleaned_data.get('social_links', '')
        if not social_links or not social_links.strip():  # Si el campo está vacío o contiene solo espacios en blanco
            return {}  # Retorna un diccionario vacío para un campo vacío
        return validate_social_links(social_links)

# Formulario personalizado para la creación de nuevos usuarios
class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para la creación de nuevos usuarios.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'form-control'}),
        help_text="Introduce un correo electrónico válido.",
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'form-control'}),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'form-control'}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario', 'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña', 'class': 'form-control'}),
        }

    def clean_email(self):
        """
        Valida que el correo no esté ya registrado.
        """
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado. Usa otro correo.")
        return email

    def clean_username(self):
        """
        Valida que el nombre de usuario no esté ya registrado.
        """
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está registrado. Elige otro.")
        return username

# Formulario para la creación de publicaciones
class PostForm(forms.ModelForm):
    """
    Formulario para la creación de publicaciones.
    """
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Escribe algo...',
                'rows': 3,
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

# Formulario para agregar comentarios a las publicaciones
class CommentForm(forms.ModelForm):
    """
    Formulario para agregar comentarios a las publicaciones.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Escribe un comentario...',
                'class': 'form-control'
            }),
        }

    def clean_content(self):
        """
        Valida que el comentario tenga al menos 3 caracteres.
        """
        content = self.cleaned_data.get('content')
        if len(content) < 3:
            raise forms.ValidationError("El comentario debe tener al menos 3 caracteres.")
        return content

# forms.py

from django import forms
from .models import Message
from django.contrib.auth import get_user_model

from django import forms
from .models import Message, CustomUser

class MessageForm(forms.ModelForm):
    receiver_username = forms.CharField(max_length=100, required=True, label='Destinatario')

    class Meta:
        model = Message
        fields = ['receiver_username', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Escribe tu mensaje...', 'rows': 4, 'class': 'form-control'}),
        }

    # Validación personalizada para el campo receiver_username
    def clean_receiver_username(self):
        username = self.cleaned_data['receiver_username']
        try:
            receiver = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError("El usuario destinatario no existe.")
        return receiver

    