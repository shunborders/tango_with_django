from django.conf.urls import patterns, url
from rango import views
#from rango.models import Category, Page

urlpatterns = patterns('',
                       # Examples:
    # url(r'^$', 'tango_with_django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^add_pages/$', views.add_pages, name='add_pages'),
    url(r'^add_pages/(?P<category_name_slug>[-\w]+)/$', views.category, name='additional_pages'),
    url(r'^Category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    #url(r'^register/$', views.register, name='register'),
    #url(r'^login/$', views.user_login, name='login'),
    url(r'^restricted/$', views.restricted, name='restricted'),
    url(r'^search/$', views.search, name='search'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^goto/$', views.track_url, name='goto'),
    url(r'^/like_category/$', views.like_category, name='like_category'),
    #url(r'^logout/$', views.user_logout, name='logout'),

    )
