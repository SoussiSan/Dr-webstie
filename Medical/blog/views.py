from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.urls import reverse

from .models import Post
from .forms import CreatePost
from account.decorators import role_required
# Create your views here.


@login_required
def blog(request):
    try:
        posts = Post.objects.all().order_by('-updated_dt')
    except:
        return redirect('error')
    user = request.user
    context = {
        'posts': posts,
        'user': user,
    }
    return render(request, 'blog.html', context)


@login_required
@role_required("DOCTOR")
def create_post(request):
    form = CreatePost()
    # all_posts = Post.objects.all().order_by('-created_dt')
    posts = Post.objects.all().order_by('-updated_dt')
    if request.method == 'POST':
        form = CreatePost(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.updated_dt = timezone.now()
            post.save()
            blog = reverse('blog')
            return redirect(blog+f'?posts={posts}')
            # return render(request, 'blog', {'posts': posts})
    return render(request, 'create_post.html', {'form': form})

