"""Unified bookmark API."""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.serializers import TaskListSerializer

from .services import (
    add_bookmark,
    get_bookmarkable_task,
    list_bookmarked_tasks,
    remove_bookmark,
    user_bookmark_task_ids,
)


class BookmarkListAPIView(APIView):
    """GET /api/v1/bookmarks/ — current user's saved listings."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        listing_kind = request.query_params.get('listing_kind')
        tasks = list_bookmarked_tasks(request.user, listing_kind)
        context = {
            'request': request,
            'user_bookmark_task_ids': user_bookmark_task_ids(request.user),
        }
        serializer = TaskListSerializer(tasks, many=True, context=context)
        return Response(serializer.data)


class BookmarkToggleAPIView(APIView):
    """POST/DELETE /api/v1/bookmarks/{slug}/ — add or remove bookmark."""

    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        task = get_bookmarkable_task(slug)
        _, created = add_bookmark(request.user, task)
        if created:
            return Response({'message': 'Bookmarked successfully.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already bookmarked.'})

    def delete(self, request, slug):
        task = get_bookmarkable_task(slug)
        if remove_bookmark(request.user, task):
            return Response({'message': 'Bookmark removed successfully.'})
        return Response({'error': 'Not bookmarked.'}, status=status.HTTP_404_NOT_FOUND)
