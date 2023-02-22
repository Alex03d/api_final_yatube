from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet

app_name = 'api'

router = DefaultRouter()
router.register(
    r'api/v1/posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register('api/v1/posts', PostViewSet, basename='posts')
router.register('api/v1/groups', GroupViewSet, basename='groups')
router.register('api/v1/follow', FollowViewSet, basename='follow')


urlpatterns = [
    path('', include(router.urls), name='api-root'),
    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.jwt')),
]
