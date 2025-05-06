from django.shortcuts import render
from rest_framework import mixins, viewsets
from .models import Prompt
from .serializers import PromptSerializer

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
        List all prompts.
        GET /api/prompts/
        Returns: 200 OK, list of prompts.
        """
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
        """
        return super().create(request, *args, **kwargs)

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
