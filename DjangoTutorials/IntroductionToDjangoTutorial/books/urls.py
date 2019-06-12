from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about),
    path('books/all/', views.get_all_books),
    path('books/detail/<int:pk>/', views.detail),
    path('books/old/', views.get_old_books),
]
