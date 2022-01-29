from pyexpat import model
from attr import field
from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    class Meta:
        model = Profile
        fields = '__all__'
        
