from django.shortcuts import render, get_object_or_404, redirect
from .forms import BlogForm
from .models import Blog


# Create your views here.

def add_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)

        if form.is_valid():
            blog_item = form.save(commit=False)  # create a new object
            blog_item.save()  # save the object
            return redirect('/blog/details/' + str(blog_item.id))

    else:
        form = BlogForm()  # create a new form

    return render(request, 'blog/blog_form.html', {'form': form})


def edit_blog(request, edit_id=None):
    blog_item = get_object_or_404(Blog, id=edit_id)
    form = BlogForm(request.POST or None, instance=blog_item)

    if form.is_valid():
        form.save()
        return redirect('/blog/details/' + str(blog_item.id))

    return render(request, 'blog/blog_form.html', {'form': form})


def blog_details(request, blog_id=id):
    blog_obj = Blog.objects.get(id=blog_id)

    return render(request, 'blog/blog_details.html', {'blog': blog_obj})

