"""
User model and manager for the users app.

This module contains the custom User model that uses email as the unique identifier
instead of username, along with its custom manager.
"""

import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail


class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as unique identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    All of the fields from AbstractUser are explicitly defined here so as to make it clear what fields are available.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this object.",
    )
    # Remove username field as we use email
    username = None

    email = models.EmailField(
        unique=True,
        verbose_name="email address",
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )

    password = models.CharField(max_length=128)

    first_name = models.CharField("first name", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=True)
    is_staff = models.BooleanField(
        "Can Access Admin Page",
        default=False,
        help_text="Designates whether the user can access the admin site. Also designates if the user is an admin on the site.",
    )

    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts.",
    )
    is_superuser = models.BooleanField(
        "Superuser Status",
        default=False,
        help_text="Designates that this user has all permissions without explicitly assigning them.",
    )

    # Group and permission relations from PermissionsMixin
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="user_set",
        related_query_name="user",
    )

    # Email verification fields
    verification_token = models.CharField(
        max_length=100, blank=True, help_text="Token for email verification"
    )
    email_verification_sent_at = models.DateTimeField(
        null=True, blank=True, help_text="When the last verification email was sent"
    )

    # Timestamp fields
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    test_scenario = models.ForeignKey(
        'test_scenario.TestScenario',
        null=True,
        blank=True,
        on_delete=models.CASCADE,  # Important: ensures test users are deleted when their scenario is deleted
        help_text="Test scenario this user is associated with (for test data isolation)."
    )

    objects = UserManager()

    # Field settings
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """String representation of user."""
        return f"{self.email}"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

