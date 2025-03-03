from django.contrib import admin

from notes.models import Note


# Register your models here.
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'user', 'private', 'pinned', 'created_at', 'updated_at', 'slug',)
    readonly_fields = ('user', 'private', 'pinned', 'created_at', 'updated_at',)