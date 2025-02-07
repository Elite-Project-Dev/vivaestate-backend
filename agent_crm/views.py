from rest_framework import viewsets, permissions, filters
from .models import Lead
from .serializers import LeadSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by('-created_at')
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'status'] 
    ordering_fields = ['created_at', 'status']
    def perform_create(self, serializer):
        serializer.save(assigned_agent=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Lead.objects.all()
        return Lead.objects.filter(assigned_agent=user)