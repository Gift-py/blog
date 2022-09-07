from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.db.models import Count
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from taggit.models import Tag

from .models import Post, Comments
from .forms import EmailPostForm, CommentForm, SearchForm


def post_list(request, tag_slug=None):
    object_list = Post.objects.all()
    tag = None
    tags = Post.tags.all()
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in = [tag])

    paginator = Paginator(object_list, 3) #3 blogs per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an integer deliver the firt page (Almost like default page)
        posts = paginator.page(1)
    except EmptyPage:
        #if page is out pf range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    return render(request, 'blog/post/list.html', {'posts':posts, 'page':page, 'tag':tag, 'tags':tags})

# class PostListView(ListView):
#     queryset =  Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


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
    
    #list of similar posts
    similar_posts = post.tags.similar_objects()
    
    return render(request, 'blog/post/detail.html', {'post':post, 'comments':comments, 'new_comment':new_comment, 'comment_form':comment_form, 'similar_posts':similar_posts})

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

def post_search(request):
    form = SearchForm()
    query = request.GET.get('search')
    results = []
    if query:
        form = SearchForm(request.GET)
        if form.is_valid():
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.001).order_by('-rank')
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results}) 


