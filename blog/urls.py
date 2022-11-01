from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from blog_app_1.sitemaps import PostSitemap

siteamps = {
    'posts':PostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog_app_1/', include('blog_app_1.urls', namespace='blog')),
    path('sitemap.xml', sitemap, {'sitemaps':siteamps}, name='dajngo.contrib.stiemaps.view.sitemap')
]
