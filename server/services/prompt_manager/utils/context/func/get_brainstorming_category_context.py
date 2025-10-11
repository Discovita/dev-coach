import os
from apps.coach_states.models import CoachState
from enums.identity_category import IdentityCategory
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")

# Map IdentityCategory values to markdown file paths
CATEGORY_CONTEXT_FILES = {
    IdentityCategory.PASSIONS: "services/prompt_manager/utils/context/identity_category_context/passions_and_talents.md",
    IdentityCategory.MONEY_MAKER: "services/prompt_manager/utils/context/identity_category_context/maker_of_money.md",
    IdentityCategory.MONEY_KEEPER: "services/prompt_manager/utils/context/identity_category_context/keeper_of_money.md",
    IdentityCategory.SPIRITUAL: "services/prompt_manager/utils/context/identity_category_context/spiritual.md",
    IdentityCategory.APPEARANCE: "services/prompt_manager/utils/context/identity_category_context/personal_appearance.md",
    IdentityCategory.HEALTH: "services/prompt_manager/utils/context/identity_category_context/physical_expression.md",
    IdentityCategory.FAMILY: "services/prompt_manager/utils/context/identity_category_context/familial_relations.md",
    IdentityCategory.ROMANTIC: "services/prompt_manager/utils/context/identity_category_context/romantic_relation.md",
    IdentityCategory.ACTION: "services/prompt_manager/utils/context/identity_category_context/doer_of_things.md",
    IdentityCategory.REVIEW: "services/prompt_manager/utils/context/identity_category_context/review.md",
}

def get_brainstorming_category_context(coach_state: CoachState) -> str:
    """
    Returns the markdown content for the currently focused identity category for the brainstorming prompt.
    """
    category = coach_state.identity_focus
    file_path = CATEGORY_CONTEXT_FILES.get(category)
    if not file_path:
        return f"No context file mapped for category: {category}"
    log.debug(f"File Path: {file_path}")
    abs_path = os.path.abspath(file_path)
    try:
        with open(abs_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Could not load context for {category}: {str(e)}" 