from django.shortcuts import render

from .models import Book

# Create your views here.


def about(request):
    return render(request, 'books/about.html')


def get_old_books(request):
    books = Book.objects.filter(in_print=False)
    return render(request, 'books/list_view.html', {'books': books, 'title': 'Out of print'})


def get_all_books(request):
    books = Book.objects.all()
    return render(request, 'books/list_view.html', {'books': books, 'title': 'All Books'})


def detail(request, **kwargs):
    book = Book.objects.get(pk=kwargs['pk'])
    return render(request, 'books/detail_view.html', {'book': book})