from enum import _auto_null
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.core.mail import send_mail

from .models import Post, Comments
from .forms import EmailPostForm, CommentForm


# def post_list(request):
#     object_list = Post.objects.all()
#     paginator = Paginator(object_list, 3) #3 blogs per page
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         #if page is not an integer deliver the firt page (Almost like default page)
#         posts = paginator.page(1)
#     except EmptyPage:
#         #if page is out pf range deliver last page of results
#         posts = paginator.page(paginator.num_pages)
#     return render(request, 'blog/post/list.html', {'posts':posts})

class PostListView(ListView):
    queryset =  Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)

    #list active comments in this post
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        #if a comment was posted,
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)   #comment created but it's not saved to the DB yet
            new_comment.post = post                                             #assign current post to comment first before saving
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post':post, 'comments':comments, 'new_comment':new_comment, 'comment_form':comment_form})


def post_share(request, post_id):
    #retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        #form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cd["name"]} recommends you to read {post.title}'
            message = f'Read {post.title} at {post_url} \n\n {cd["name"]}\'s comment: {cd["comments"]}'
            send_mail(subject, message, 'jesuobohgift@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent})

