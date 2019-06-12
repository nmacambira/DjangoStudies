# from django.conf.urls import url, include
# from rest_framework.urlpatterns import format_suffix_patterns
#
# from . import views
#
# # urlpatterns = [
# #     url(r'^snippets/$', views.SnippetList.as_view()),
# # ]
# #
# # urlpatterns = format_suffix_patterns(urlpatterns)
#
#
# # API endpoints
# urlpatterns = format_suffix_patterns([
#     url(r'^$', views.api_root),
#     url(r'^api-auth/',
#         include('rest_framework.urls')),
#     url(r'^snippets/$',
#         views.SnippetList.as_view(),
#         name='snippet-list'),
#     url(r'^snippets/(?P<pk>[0-9]+)/$',
#         views.SnippetDetail.as_view(),
#         name='snippet-detail'),
#     url(r'^snippets/(?P<pk>[0-9]+)/highlight/$',
#         views.SnippetHighlight.as_view(),
#         name='snippet-highlight'),
#     url(r'^users/$',
#         views.UserList.as_view(),
#         name='user-list'),
#     url(r'^users/(?P<pk>[0-9]+)/$',
#         views.UserDetail.as_view(),
#         name='user-detail')
# ])

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
]