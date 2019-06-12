from django.contrib import admin

from .models import Book, Publisher, Author, Genre

# Register your models here.


class BookAdmin(admin.ModelAdmin):
    pass


class PublisherAdmin(admin.ModelAdmin):
    pass


class AuthorAdmin(admin.ModelAdmin):
    pass


class GenreAdmin(admin.ModelAdmin):
    pass


admin.site.register(Book, BookAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre, GenreAdmin)
