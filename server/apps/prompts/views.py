from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from .models import Prompt
from .serializers import PromptSerializer
from rest_framework.decorators import action

# Create your views here.


class PromptViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint for managing Prompts.

    Supported operations:
    - list:    GET    /api/prompts/         List all prompts
    - retrieve:GET    /api/prompts/{id}/    Retrieve a single prompt by ID
    - create:  POST   /api/prompts/         Create a new prompt
    - update:  PUT    /api/prompts/{id}/    Update a prompt (full update)
    - partial_update:PATCH /api/prompts/{id}/ Partial update of a prompt
    - destroy: DELETE /api/prompts/{id}/    Delete a prompt

    Returns all fields of the Prompt model. See PromptSerializer for details.
    """

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer

    def list(self, request, *args, **kwargs):
        """
        List all prompts (only those with is_active=True).
        GET /api/prompts/
        Returns: 200 OK, list of active prompts.
        """
        self.queryset = Prompt.objects.filter(is_active=True)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single prompt by ID.
        GET /api/prompts/{id}/
        Returns: 200 OK, prompt object.
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new prompt.
        POST /api/prompts/
        Body: Prompt fields (see PromptSerializer)
        Returns: 201 Created, created prompt object.
        Automatically assigns the next version number for the given coach_state.
        Ignores any version sent from the frontend.
        """
        data = request.data.copy()
        coach_state = data.get("coach_state")
        if coach_state:
            # Find the latest version for this coach_state
            latest = Prompt.objects.filter(coach_state=coach_state).order_by("-version").first()
            data["version"] = (latest.version + 1) if latest else 1
        else:
            data["version"] = 1  # fallback, should not happen if coach_state is required
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update a prompt (full update).
        PUT /api/prompts/{id}/
        Body: All prompt fields (see PromptSerializer)
        Returns: 200 OK, updated prompt object.
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a prompt.
        PATCH /api/prompts/{id}/
        Body: Partial prompt fields (see PromptSerializer)
        Returns: 200 OK, updated prompt object.
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a prompt.
        DELETE /api/prompts/{id}/
        Returns: 204 No Content.
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="soft_delete")
    def soft_delete(self, request, pk=None):
        """
        Soft delete a prompt: set is_active to False instead of deleting.
        POST /api/prompts/{id}/soft_delete/
        Returns: 200 OK, updated prompt object with is_active=False.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
