from django.contrib import admin
from .models import CustomUser, Profile, JobPost, JobApplication, Project
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_role', 'points', 'location']
    list_editable = ['points']
    list_filter = ['user__role']

    def get_role(self, obj):
        Role=client
        return obj.user.role
    get_role.short_description = 'Role'

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role']
    list_filter = ['role']
    readonly_fields = ['role']
    
admin.site.register(JobPost)
admin.site.register(JobApplication)
admin.site.register(Project)