from django.db import models


class IdentityCategory(models.TextChoices):
    """
    Enum for the possible categories of identity in the coaching system.
    """

    PASSIONS = "passions_and_talents", "Passions and Talents"
    MONEY_MAKER = "maker_of_money", "Maker of Money"
    MONEY_KEEPER = "keeper_of_money", "Keeper of Money"
    SPIRITUAL = "spiritual", "Spiritual"
    APPEARANCE = "personal_appearance", "Personal Appearance"
    HEALTH = "physical_expression", "Physical Expression"
    FAMILY = "familial_relations", "Familial Relations"
    ROMANTIC = "romantic_relation", "Romantic Relation"
    ACTION = "doer_of_things", "Doer of Things"

    @classmethod
    def from_string(cls, value: str) -> "IdentityCategory":
        """
        Convert a string to an IdentityCategory enum value, accepting flexible input.
        """
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name.lower() == normalized or member.value.lower() == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(
            f"Unknown identity category: {value}. Valid categories: {valid_types}"
        )

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the identity category.
        """
        return self.label
