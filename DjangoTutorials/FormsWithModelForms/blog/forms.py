from django.forms import ModelForm
from .models import Blog


class BlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'description']
        #fields = '__all__'  # user  if you want to use all the fields from the model in the form
        #exclude = ['title'] # if you want to user all the fields from the model, but the title