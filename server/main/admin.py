from django.contrib import admin
from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'is_active']
    list_display_links = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name', 'permissions__name')

    class Meta:
        model = Profile
        fields = '__all__'
        
        
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    class Meta:
        model = Permission
        fields = '__all__'

@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):
    list_display = ['port', 'bio', 'permission',]
    list_display_links = ('port', 'bio')
    search_fields = ('port', 'bio', 'permission__name', 'permission__bio')

    class Meta:
        model = Lock
        fields = '__all__'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['profile', 'lock', 'date_time']
    list_display_links = ('profile', 'lock')
    search_fields = ('profile__first_name','profile__last_name', 'lock__port')
    fields = ['profile', 'lock']
    readonly_fields = ['profile', 'lock', 'date_time']
    