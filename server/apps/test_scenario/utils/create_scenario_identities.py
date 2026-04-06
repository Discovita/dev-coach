"""
create_scenario_identities

Create Identity objects for a test scenario from the template's ``identities``
section, returning a name-keyed mapping for downstream use.
"""

from apps.identities.models import Identity
from apps.test_scenario.utils.copy_image_from_url import copy_image_from_url


def create_scenario_identities(scenario, template: dict, user) -> dict:
    """
    Delete existing scenario identities, then create fresh ones from the template.

    Args:
        scenario: The TestScenario instance these identities belong to.
        template: The full scenario template dict. Must contain an ``identities``
            key with a list of identity dicts.
        user: The User instance to assign the identities to.

    Returns:
        A dict mapping identity ``name`` → ``Identity`` instance for all
        created identities.

    Raises:
        ValueError: If ``user`` has no valid PK (creation was skipped or failed).
    """
    if not user or not user.id:
        raise ValueError(
            "Cannot create identities: user creation failed or was skipped"
        )

    Identity.objects.filter(user=user, test_scenario=scenario).delete()
    created: dict[str, Identity] = {}

    for identity_data in template["identities"]:
        identity = Identity(
            user=user,
            test_scenario=scenario,
            name=identity_data.get("name"),
            category=identity_data.get("category"),
            state=identity_data.get("state"),
            i_am_statement=identity_data.get("i_am_statement", ""),
            visualization=identity_data.get("visualization", ""),
            notes=identity_data.get("notes", []),
        )

        image_url = identity_data.get("image")
        if image_url:
            copied_key = copy_image_from_url(image_url)
            if copied_key:
                image_path = (
                    copied_key[6:] if copied_key.startswith("media/") else copied_key
                )
                identity.image.name = image_path

        identity.save()
        created[identity.name] = identity

    return created
