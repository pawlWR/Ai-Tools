from django.contrib import admin
from .models import Thread, ThreadMessage,Product,Sales,SalesItem


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

class SalesItemInline(admin.TabularInline):
    model = SalesItem

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    inlines = [SalesItemInline]
    list_display = ('name', 'email', 'phone', 'address', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone', 'address')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'price')

