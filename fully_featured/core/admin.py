from django.contrib import admin

from .models import ToDo, ToDoGroup, Journal, JournalGroup, Note, NoteGroup, Term, TermGroup


@admin.register(ToDo)
class ToDoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'user',
        'title',
        'description',
        'completed',
        'group',
    )
    list_filter = ('created_at', 'updated_at', 'user', 'completed', 'group')
    date_hierarchy = 'created_at'


@admin.register(ToDoGroup)
class ToDoGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'user', 'name')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'user',
        'text',
        'group',
    )
    list_filter = ('created_at', 'updated_at', 'user', 'group')
    date_hierarchy = 'created_at'


@admin.register(JournalGroup)
class JournalGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'user', 'name')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'user',
        'title',
        'text',
        'group',
    )
    list_filter = ('created_at', 'updated_at', 'user', 'group')
    date_hierarchy = 'created_at'


@admin.register(NoteGroup)
class NoteGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'user', 'name')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'user',
        'term',
        'definition',
        'group',
    )
    list_filter = ('created_at', 'updated_at', 'user', 'group')
    date_hierarchy = 'created_at'


@admin.register(TermGroup)
class TermGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'user', 'name')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('name',)
    date_hierarchy = 'created_at'
