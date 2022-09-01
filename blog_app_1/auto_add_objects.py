from django.contrib.auth.models import User
from blog_app_1.models import Post
import random

users = User.objects.all()

def add():
    for i in range(30):
        user = random.choice(users)
        post = Post(title=f'Dummy Post {i+1}', slug=f'dummy-post-{i+1}', body='This is a dummy post', author=user, status='published')
        post.save()



add()
print('done')