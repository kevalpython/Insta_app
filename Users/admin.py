from django.contrib import admin
from .models import User

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    This class displays user data in the admin panel.
    """

    list_display = ["id","username", "first_name","last_name", "email",'profile_img']
    
