from django.contrib import admin
from .models import UserProfile, Post

class UserProfileAdmin(admin.ModelAdmin):
    # Mostrar campos personalizados en el admin
    list_display = ('user', 'get_first_name', 'get_last_name', 'phone', 'bio')
    
    # Definir métodos para mostrar el nombre y apellido del usuario
    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.admin_order_field = 'user__first_name'  # Permite ordenar por 'first_name' en el admin
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.admin_order_field = 'user__last_name'  # Permite ordenar por 'last_name' en el admin
    get_last_name.short_description = 'Last Name'
    
    # Agregar opciones de búsqueda y filtros (opcional)
    search_fields = ('user__username', 'user__email', 'phone')  # Permite buscar por nombre de usuario, correo y teléfono
    list_filter = ('user__is_active', 'user__is_staff')  # Filtro por estado de usuario y si es staff

# Registrar los modelos en el admin
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Post)
