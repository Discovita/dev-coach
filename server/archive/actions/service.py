"""Service for managing OpenAI function definitions."""

from typing import List
from .models import (
    FunctionDefinition,
    CreateIdentityParams,
    UpdateIdentityParams,
    AcceptIdentityParams,
    AcceptIdentityRefinementParams,
    AddIdentityNoteParams,
    TransitionStateParams,
    SelectIdentityFocusParams
)

class ActionDefinitionService:
    """Service for managing OpenAI function definitions."""
    
    def get_function_definitions(self) -> List[FunctionDefinition]:
        """Get all available function definitions."""
        return [
            FunctionDefinition(
                name="create_identity",
                description="Create a new identity during brainstorming",
                parameters=CreateIdentityParams.model_json_schema()
            ),
            FunctionDefinition(
                name="update_identity",
                description="Update an identity during refinement",
                parameters=UpdateIdentityParams.model_json_schema()
            ),
            FunctionDefinition(
                name="accept_identity",
                description="Mark an identity as accepted",
                parameters=AcceptIdentityParams.model_json_schema()
            ),
            FunctionDefinition(
                name="accept_identity_refinement",
                description="Mark an identity as refinement complete",
                parameters=AcceptIdentityRefinementParams.model_json_schema()
            ),
            FunctionDefinition(
                name="add_identity_note",
                description="Add a note to an identity",
                parameters=AddIdentityNoteParams.model_json_schema()
            ),
            FunctionDefinition(
                name="select_identity_focus",
                description="Select an identity to focus on during refinement",
                parameters=SelectIdentityFocusParams.model_json_schema()
            ),
            FunctionDefinition(
                name="transition_state",
                description="Request a state transition",
                parameters=TransitionStateParams.model_json_schema()
            )
        ]
    
    def get_openai_schema(self) -> List[dict]:
        """Get function definitions in OpenAI schema format."""
        return [
            definition.model_dump()
            for definition in self.get_function_definitions()
        ]
