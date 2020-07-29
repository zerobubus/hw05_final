from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


@cache_page(20, key_prefix="index_page")
def index(request):

    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)  
    page_number = request.GET.get("page")  
    page = paginator.get_page(page_number)  
    return render(
        request,
        "index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)  
    page_number = request.GET.get("page")  
    page = paginator.get_page(page_number)  
    return render(
        request,
        "group.html", 
        {"page": page, 
        "paginator": paginator, 
        "group": group }
    )        


@login_required
def new_post(request):

    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, "new_post.html", {"form": form})      
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")  

 
def profile(request, username):
        
    author = get_object_or_404(User, username=username)
    pages = author.authors.all()
    post_count = author.authors.count()
    paginator = Paginator(pages, 10) 
    page_number = request.GET.get("page")  
    page = paginator.get_page(page_number) 
    following = Follow.objects.filter(author=author)
    follower = Follow.objects.filter(user=author)
    following_count = following.count()
    follower_count = follower.count()
        
    return render(
        request,
        "profile.html",
        {"post_count": post_count,
        "page": page, 
        "author": author,
        "username": username,
        "following": following,
        "following_count": following_count,
        "follower_count": follower_count,
        "paginator": paginator}
    )
    
           
def post_view(request, username, post_id):
        
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author
    form = CommentForm(instance=None)
    items = post.comments.all()
    return render(
        request, 
        "post.html", 
        {"post": post, 
        "author": author,
        "form": form,
        "items": items 
        }
    )


@login_required()
def post_edit(request, username, post_id):

    post = Post.objects.get(id=post_id, author__username=username)
    if request.user != post.author:
        return redirect(f"/{post.author}/{post_id}")
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if not form.is_valid():
        return render(
            request, 
            "post_new.html",
            {"post": post, 
            "form": form}
        )  
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(f"/{post.author}/{post_id}")

    
def page_not_found(request, exception):
    
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )

def server_error(request):
    return render(request, "misc/500.html", status=500)   


@login_required()
def add_comment(request, username, post_id):

    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(
            request, 
            "post.html",
            {"form": form, "post": post}
        )   
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    return redirect("post", username=username, post_id=post.id)    


@login_required
def follow_index(request):
    
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {"page": page, 
        "paginator": paginator}
    )


@login_required
def profile_follow(request, username):

    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user, author=author).exists()
    if following or request.user == author:
        return redirect("profile", username=username)
    follower = Follow.objects.create(user=request.user, author=author)
    follower.save()
    return redirect("profile", username=username)
        

@login_required
def profile_unfollow(request, username):
    
    author = get_object_or_404(User, username=username)
    un_follow = Follow.objects.filter(user=request.user, author=author)
    un_follow.delete()
    return redirect("profile", username=username)

