from django.urls import path
from . import views

urlpatterns = [
    path('blog/add', views.add_blog, name='add_blog'),
    path('blog/edit/<int:edit_id>', views.edit_blog, name='edit_blog'),
    path('blog/details/<int:blog_id>', views.blog_details, name='blog_details'),
]