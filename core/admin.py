from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

# -----------------
# USER CUSTOMIZADO
# -----------------
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "is_active", "is_staff", "is_superuser", "grupo"
        )


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("username", "email", "grupo", "is_staff", "is_active")
    list_filter = ("grupo", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informações pessoais", {"fields": ("first_name", "last_name", "email", "grupo")}),
        ("Permissões", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Datas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "password1", "password2",
                "grupo", "is_staff", "is_active"
            )}
        ),
    )

    search_fields = ("username", "email")
    ordering = ("username",)

# -------------
# ADMIN PADRÃO
# -------------
class DefaultAdmin(admin.ModelAdmin):
    ordering = ("id",)

    def get_list_display(self, request):
        """
        Lista colunas automaticamente:
        - id
        - nome / titulo / codigo (se existirem)
        - campos de auditoria (created_at / updated_at / data_criacao / data_atualizacao)
        - __str__
        """
        fields = []

        if hasattr(self.model, "id"):
            fields.append("id")

        for col in ["nome", "titulo", "codigo"]:
            if hasattr(self.model, col):
                fields.append(col)

        for extra in ["created_at", "updated_at", "data_criacao", "data_atualizacao"]:
            if hasattr(self.model, extra):
                fields.append(extra)

        fields.append("__str__")
        return fields

admin.site.register(User, CustomUserAdmin)
admin.site.register(Municipio)
admin.site.register(Parada)
admin.site.register(Irrigantes)
admin.site.register(CategoriaDocumento)
admin.site.register(Documento)
admin.site.register(Projeto)
admin.site.register(Manifestacao)
