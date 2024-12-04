from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--vcj@(3o$fuhdvse40_cau76qn!bo6sarh2^kg6&l4-(gt$b96'

# SECURITY WARNING: Don't run with debug turned on in production!
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.0.6', '0.0.0.0', '172.16.154.246', '192.168.0.2', '172.16.117.110', '172.20.10.3', '172.16.152.8']
  # Añadir tus dominios en producción
# settings.py
SITE_URL = 'http://127.0.0.1:8000'  # Para desarrollo local

# Application definition
INSTALLED_APPS = [
    # Aplicaciones de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones personalizadas
    'posts',  # Tu app personalizada
    'channels',
    'sslserver', 
     'django_extensions',  # Para servir aplicaciones en un entorno seguro
]

# Configuración de Channels
ASGI_APPLICATION = 'facetruck.asgi.application'

# Configuración de Redis (asegúrate de tener Redis instalado en tu entorno)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'facetruck.urls'

# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Carpeta para plantillas personalizadas
        'APP_DIRS': True,  # Esto buscará plantillas dentro de tus apps también
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'facetruck.wsgi.application'

# Email backend (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'admin@facetruck.com'  # Cambiar para producción

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom user model
AUTH_USER_MODEL = 'posts.CustomUser'

# Media files settings (user-uploaded files)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Asegurarse de que la ruta sea correcta
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Asegúrate de que 'media' exista en tu directorio BASE_DIR

STATIC_ROOT = BASE_DIR / "staticfiles"  # Archivos estáticos recopilados para producción

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es'  # Cambiar a 'es' para español
TIME_ZONE = 'UTC'  # Cambiar a tu zona horaria local, por ejemplo, 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Login and logout redirection
LOGIN_REDIRECT_URL = '/'  # Redirigir al inicio después de iniciar sesión
LOGOUT_REDIRECT_URL = '/'  # Redirigir al inicio después de cerrar sesión

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Seguridad para producción
SECURE_SSL_REDIRECT = False  # Asegúrate de que se redirijan todas las solicitudes a HTTPS en producción
CSRF_COOKIE_SECURE = True  # Solo se enviarán las cookies CSRF a través de HTTPS
