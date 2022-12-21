from django.contrib import admin
from .models import Inio, Category

class InioAdmin(admin.ModelAdmin):
    list_display = ['domain', 'description', 'status', 'created', 'updated']
    search_fields = ['domain', 'description', 'status']
    ordering = ['-updated','-created']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_text']
    search_fields = ['category_text']
    ordering = ['category_text']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Inio, InioAdmin)
