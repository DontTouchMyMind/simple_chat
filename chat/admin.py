from django.contrib import admin

from chat.models import User


class ChatAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'user_status']
    actions = ['ban_user', 'unban_user']

    @staticmethod
    def ban_user(request, queryset):
        queryset.update(status='b')

    ban_user.short_description = 'Mark selected user as banned'

    @staticmethod
    def unban_user(request, queryset):
        queryset.update(status='a')

    unban_user.short_description = 'Mark selected user as unbanned'


admin.site.register(User, ChatAdmin)
