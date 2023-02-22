from django.shortcuts import get_object_or_404
from posts.models import Comment, Group, Post, User, Follow
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
# from rest_framework.pagination import LimitOffsetPagination

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (CommentSerializer,
                          GroupSerializer,
                          PostSerializer,
                          FollowSerializer
                          )


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = (IsAuthorOrReadOnlyPermission, IsAuthenticated,)
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnlyPermission
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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
        follow, created = Follow.objects.get_or_create(
            user=user,
            author=following_user
        )
        if not created:
            return Response({'error': 'already following this user'})

        serializer = self.serializer_class(follow)
        return Response(serializer.data)
