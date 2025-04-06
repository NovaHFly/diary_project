from django.contrib import admin

from . import models


@admin.register(models.Note)
class Note(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    list_display_links = ['title']
    search_fields = ['title']


@admin.register(models.Tag)
class Tag(admin.ModelAdmin):
    list_display = ['name', 'author']
    list_display_links = ['name']
    search_fields = ['name']
