from django.shortcuts import get_object_or_404
from posts.models import Comment, Group, Post
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.response import Response

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (CommentSerializer,
                          GroupSerializer,
                          PostSerializer,
                          FollowSerializer
                          )
# from .pagination import CustomPagination


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = (IsAuthorOrReadOnlyPermission, IsAuthenticated,)
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnlyPermission
    )
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    #
    # def create(self, request, *args, **kwargs):
    #     serializer = GroupSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(
    #             serializer.errors,
    #             status=status.HTTP_400_BAD_REQUEST
    #         )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnlyPermission,
    )
    # permission_classes = (IsAuthorOrReadOnlyPermission, IsAuthenticated,)

    def get_queryset(self):
        return Comment.objects.filter(post=self.kwargs.get('post_id'))

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'post')


# class FollowViewSet(viewsets.ViewSet):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = FollowSerializer
#
#     def create(self, request):
#         following_username = request.data.get('following')
#         if following_username is None:
#             return Response({'error': 'following username is required'})
#         following_user = get_object_or_404(User, username=following_username)
#         user = request.user
#         if user == following_user:
#             return Response({'error': 'cannot follow yourself'})
#         follow, created = Follow.objects.get_or_create(
#             user=user,
#             author=following_user
#         )
#         if not created:
#             return Response({'error': 'already following this user'})
#
#         serializer = self.serializer_class(follow)
#         return Response(serializer.data)
class FollowViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
