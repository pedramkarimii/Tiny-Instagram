from django.contrib import admin
from account.models import User, Profile, OptCode
from .forms import UserChangeForm, ProfileForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class ProfileInline(admin.StackedInline):
    """
    Defines inline admin options for the Profile model.
    """
    model = Profile
    add_form = ProfileForm
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Defines admin options for the Profile model.
    """
    model = Profile
    list_display = ('user', 'full_name', 'gender', 'followers', 'following')
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('-update_time',)
    row_id_fields = ('user',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Customizes the User admin interface.
    """
    form = UserChangeForm
    # add_form = ChangePasswordForm
    model = User
    list_display = ('username', 'email', 'phone_number', 'is_admin', 'is_superuser', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_active')
    fieldsets = (
        ('Change personal info', {'fields': ('email', 'phone_number', 'username', 'password')}),
        ('Permissions',
         {'fields': (
             'is_superuser', 'is_active', 'is_admin', 'is_staff', 'is_deleted', 'create_time', 'update_time',
             'last_login',
             'groups', 'user_permissions')}),

    )

    add_fieldsets = (
        ('Creation User', {
            'fields': ('email', 'phone_number', 'username', 'password1', 'password2')}
         ),
    )
    row_id_fields = ('phone_number',)
    readonly_fields = ('create_time', 'update_time', 'last_login')
    search_fields = ('email',)
    ordering = ('-create_time',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the form based on the requesting user's permissions.

        Args:
            request: The HTTP request object.
            obj: The object being edited (if any).
            **kwargs: Additional keyword arguments.

        Returns:
            Form: The customized form.
        """
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser and 'is_superuser' in form.base_fields:
            form.base_fields["is_superuser"].disabled = True
            form.base_fields["is_admin"].disabled = True
            form.base_fields["is_staff"].disabled = True
            form.base_fields["is_active"].disabled = True
            form.base_fields["is_deleted"].disabled = True
        return form

    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        """
        Overrides the get_inline_instances method to conditionally display
        the inline based on whether an object is being edited.
        """
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(OptCode)
class OptCodeAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing OptCode model.
    """
    model = OptCode
    list_display = ('code', 'email', 'phone_number', 'created')
    search_fields = ('phone_number',)
    ordering = ('created',)
    row_id_fields = ('phone_number',)
