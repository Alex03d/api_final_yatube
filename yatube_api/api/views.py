from django.shortcuts import get_object_or_404
from posts.models import Comment, Group, Post, User, Follow
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import CommentSerializer, GroupSerializer, PostSerializer, FollowSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, IsAuthenticated,)

    def get_queryset(self):
        return Comment.objects.filter(post=self.kwargs.get('post_id'))

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer

    def create(self, request):
        following_username = request.data.get('following')
        if following_username is None:
            return Response({'error': 'following username is required'})
        following_user = get_object_or_404(User, username=following_username)
        user = request.user
        if user == following_user:
            return Response({'error': 'cannot follow yourself'})
        follow, created = Follow.objects.get_or_create(user=user, author=following_user)
        if not created:
            return Response({'error': 'already following this user'})

        serializer = self.serializer_class(follow)
        return Response(serializer.data)


# class FollowViewSet(viewsets.ModelViewSet):
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer
#     permission_classes = (IsAuthenticated,)
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
#
#     def create(self, request, *args, **kwargs):
#         author_id = request.data.get('author')
#         if author_id is None:
#             return Response({'author': ['This field is required.']}, status=400)
#
#         if author_id == self.request.user.id:
#             return Response({'author': ['You cannot follow yourself.']}, status=400)
#
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         if Follow.objects.filter(user=self.request.user, author_id=author_id).exists():
#             return Response({'author': ['You already follow this user.']}, status=400)
#
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=201, headers=headers)
