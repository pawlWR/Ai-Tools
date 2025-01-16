from django.contrib import admin
from .models import Thread, ThreadMessage

class ThreadMessageInline(admin.TabularInline):
    model = ThreadMessage

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    inlines = [ThreadMessageInline]
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', )

@admin.register(ThreadMessage)
class ThreadMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'response', 'created_at', 'updated_at')
    search_fields = ('content', 'response')
