from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FaqItem
from .serializers import FaqItemSerializer


class FaqListAPIView(APIView):
    """
    GET /faq/
    Public FAQ list. Optional query: ?category=services|general
    """

    permission_classes = [AllowAny]

    def get(self, request):
        queryset = FaqItem.objects.filter(is_published=True)
        category = (request.query_params.get('category') or '').strip().lower()
        if category:
            queryset = queryset.filter(category=category)

        items = queryset.order_by('sort_order', 'question')
        data = FaqItemSerializer(items, many=True).data
        return Response({
            'count': len(data),
            'results': data,
        })
