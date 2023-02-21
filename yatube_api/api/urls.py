from django.urls import include, path
# from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, GroupViewSet, PostViewSet, FollowViewSet

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
    # path('api/v1/api-token-auth/', views.obtain_auth_token),
    path('auth/', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.jwt')),
]
