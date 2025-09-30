from django.contrib import admin
from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone', 'city', 'tg_chat_id',) # Отображаемые поля
    list_filter = ('city',) # возможность фильтрации
    search_fields = ('email', 'tg_chat_id',) # поиск объектов по заданным полям

