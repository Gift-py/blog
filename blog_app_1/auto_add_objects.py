from django.contrib.auth.models import User
from blog_app_1.models import Post

def add(userr):
    user = User.objects.get(username=userr)

    for i in range(5):
        post = Post(title=f'Dummy Post {i+30}', slug=f'dummy-post-{i+30}', body='This is a dummy post', author=user, status='published')
        post.save()


add('gift')
print('done')