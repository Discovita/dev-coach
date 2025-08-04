from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from .models import Action
from .serializer import ActionSerializer, ActionListSerializer


class ActionFilter(filters.FilterSet):
    """
    Filter for Action model.
    Allows filtering by action_type, user, and test_scenario.
    """
    action_type = filters.CharFilter(field_name='action_type', lookup_expr='exact')
    user = filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    test_scenario = filters.NumberFilter(field_name='test_scenario__id', lookup_expr='exact')
    
    class Meta:
        model = Action
        fields = ['action_type', 'user', 'test_scenario']


class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Action model.
    Provides read-only access to actions with filtering capabilities.
    
    Used in: Admin interface, action history, conversation reconstruction
    Referenced in: Coach state visualizer, debugging tools
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ActionSerializer
    filterset_class = ActionFilter
    
    def get_queryset(self):
        """
        Return actions for the current user or for admin users.
        """
        if self.request.user.is_staff:
            # Admin users can see all actions
            return Action.objects.all().order_by('-timestamp')
        else:
            # Regular users can only see their own actions
            return Action.objects.filter(user=self.request.user).order_by('-timestamp')
    
    def get_serializer_class(self):
        """
        Use different serializers for list vs detail views.
        """
        if self.action == 'list':
            return ActionListSerializer
        return ActionSerializer
    
    @action(detail=False, methods=['get'], url_path='for-user')
    def for_user(self, request):
        """
        Get actions for a specific user (admin only).
        """
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"detail": "Not authorized."}, status=403)
        
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"detail": "user_id is required."}, status=400)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(pk=user_id)
            actions = Action.objects.filter(user=user).order_by('-timestamp')
            serializer = self.get_serializer(actions, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
    
    @action(detail=False, methods=['get'], url_path='by-coach-message')
    def by_coach_message(self, request):
        """
        Get actions triggered by a specific coach message.
        """
        message_id = request.query_params.get('message_id')
        if not message_id:
            return Response({"detail": "message_id is required."}, status=400)
        
        from apps.chat_messages.models import ChatMessage
        
        try:
            message = ChatMessage.objects.get(id=message_id)
            # Ensure user can only see actions for their own messages (unless admin)
            if not request.user.is_staff and message.user != request.user:
                return Response({"detail": "Not authorized."}, status=403)
            
            actions = Action.objects.filter(coach_message=message).order_by('timestamp')
            serializer = self.get_serializer(actions, many=True)
            return Response(serializer.data)
        except ChatMessage.DoesNotExist:
            return Response({"detail": "Message not found."}, status=404)
