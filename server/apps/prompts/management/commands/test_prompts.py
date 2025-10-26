"""
Management command to test prompt rendering.
This bypasses Django's test database and tests against your live database.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.chat_messages.models import ChatMessage
from apps.prompts.models import Prompt
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState
from enums.message_role import MessageRole
from services.prompt_manager.manager import PromptManager

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to test prompt rendering.
    This bypasses Django's test database and tests against the live database.
    """

    help = "Test prompt rendering for all coaching phases"

    def add_arguments(self, parser):
        parser.add_argument(
            "--phase",
            type=str,
            help="Test specific phase only (e.g., system_context, introduction)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Testing prompt rendering...")

        # Create test user
        user, created = User.objects.get_or_create(
            email="test@example.com", defaults={"password": "testpass123"}
        )

        # Create coach state
        coach_state, created = CoachState.objects.get_or_create(
            user=user,
            defaults={
                "current_phase": CoachingPhase.INTRODUCTION,
                "identity_focus": IdentityCategory.PASSIONS.value,
                "skipped_identity_categories": [],
                "who_you_are": [],
                "who_you_want_to_be": [],
                "asked_questions": [],
            },
        )

        # Create test identities
        self._create_test_identities(user)

        # Create test chat messages
        self._create_test_chat_messages(user)

        # Test prompts
        phases_to_test = [
            CoachingPhase.SYSTEM_CONTEXT,
            CoachingPhase.INTRODUCTION,
            CoachingPhase.IDENTITY_WARMUP,
            CoachingPhase.GET_TO_KNOW_YOU,
            CoachingPhase.IDENTITY_BRAINSTORMING,
            CoachingPhase.BRAINSTORMING_REVIEW,
            CoachingPhase.IDENTITY_REFINEMENT,
            CoachingPhase.I_AM_STATEMENT,
            CoachingPhase.IDENTITY_VISUALIZATION,
        ]

        if options["phase"]:
            try:
                phase = CoachingPhase.from_string(options["phase"])
                phases_to_test = [phase]
            except:
                self.stdout.write(
                    self.style.ERROR(f"Invalid phase: {options['phase']}")
                )
                return

        results = []
        for phase in phases_to_test:
            if phase == CoachingPhase.IDENTITY_BRAINSTORMING:
                # Test brainstorming for each category
                for category in IdentityCategory:
                    success, error, prompt_info = self._test_brainstorming_phase(
                        user, coach_state, category
                    )
                    results.append(
                        {
                            "phase": f"{phase.label} ({category.label}){prompt_info}",
                            "success": success,
                            "error": error,
                        }
                    )
            else:
                success, error, prompt_info = self._test_phase(user, coach_state, phase)
                results.append(
                    {
                        "phase": f"{phase.label}{prompt_info}",
                        "success": success,
                        "error": error,
                    }
                )

        # Report results
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("PROMPT RENDERING TEST RESULTS")
        self.stdout.write("=" * 60)

        passed = 0
        failed = 0

        for result in results:
            if result["success"]:
                self.stdout.write(self.style.SUCCESS(f"✅ {result['phase']}: PASSED"))
                passed += 1
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {result['phase']}: FAILED - {result['error']}"
                    )
                )
                failed += 1

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"SUMMARY: {passed} passed, {failed} failed")
        self.stdout.write("=" * 60)

        # Show detailed error report for failed tests
        if failed > 0:
            self.stdout.write(self.style.ERROR(f"\n❌ {failed} tests failed!"))
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("DETAILED ERROR REPORT")
            self.stdout.write("=" * 60)

            for result in results:
                if not result["success"]:
                    self.stdout.write(f"\n🔍 {result['phase']}:")
                    self.stdout.write(f"   Error: {result['error']}")
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ All {passed} tests passed!"))

    def _create_test_identities(self, user):
        """Create test identities for the user."""
        categories = [
            IdentityCategory.PASSIONS,
            IdentityCategory.MONEY_MAKER,
            IdentityCategory.MONEY_KEEPER,
            IdentityCategory.SPIRITUAL,
            IdentityCategory.APPEARANCE,
            IdentityCategory.HEALTH,
            IdentityCategory.FAMILY,
            IdentityCategory.ROMANTIC,
            IdentityCategory.ACTION,
        ]

        for i, category in enumerate(categories):
            Identity.objects.get_or_create(
                user=user,
                name=f"Test Identity {i+1}",
                category=category.value,
                defaults={
                    "i_am_statement": f"I am a test {category.label} identity",
                    "visualization": f"I see myself as a test {category.label} identity",
                    "state": IdentityState.ACCEPTED,
                },
            )

    def _create_test_chat_messages(self, user):
        """Create test chat messages."""
        if not ChatMessage.objects.filter(user=user).exists():
            ChatMessage.objects.create(
                user=user,
                role=MessageRole.USER,
                content="I'm ready to start my coaching journey.",
            )
            ChatMessage.objects.create(
                user=user,
                role=MessageRole.COACH,
                content="Great! Let's explore your identities.",
            )

    def _test_phase(self, user, coach_state, phase):
        """Test a specific coaching phase."""
        try:
            # Update coach state to the target phase
            coach_state.current_phase = phase.value
            coach_state.save()

            # Get prompt info for reporting
            prompt = (
                Prompt.objects.filter(coaching_phase=phase.value, is_active=True)
                .order_by("-version")
                .first()
            )

            prompt_info = (
                f" (Prompt v{prompt.version})" if prompt else " (No prompt found)"
            )

            # Create prompt manager and test
            prompt_manager = PromptManager()
            coach_prompt, response_format = prompt_manager.create_chat_prompt(
                user=user, model="gpt-4o"
            )

            return True, None, prompt_info

        except Exception as e:
            # Get prompt info even for failed tests
            prompt = (
                Prompt.objects.filter(coaching_phase=phase.value, is_active=True)
                .order_by("-version")
                .first()
            )
            prompt_info = (
                f" (Prompt v{prompt.version})" if prompt else " (No prompt found)"
            )
            return False, str(e), prompt_info

    def _test_brainstorming_phase(self, user, coach_state, category):
        """Test identity brainstorming for a specific category."""
        try:
            # Update coach state to brainstorming phase with specific focus
            coach_state.current_phase = CoachingPhase.IDENTITY_BRAINSTORMING.value
            coach_state.identity_focus = category.value
            coach_state.save()

            # Get prompt info for reporting
            prompt = (
                Prompt.objects.filter(
                    coaching_phase=CoachingPhase.IDENTITY_BRAINSTORMING.value,
                    is_active=True,
                )
                .order_by("-version")
                .first()
            )

            prompt_info = (
                f" (Prompt v{prompt.version})" if prompt else " (No prompt found)"
            )

            # Create prompt manager and test
            prompt_manager = PromptManager()
            coach_prompt, response_format = prompt_manager.create_chat_prompt(
                user=user, model="gpt-4o"
            )

            return True, None, prompt_info

        except Exception as e:
            # Get prompt info even for failed tests
            prompt = (
                Prompt.objects.filter(
                    coaching_phase=CoachingPhase.IDENTITY_BRAINSTORMING.value,
                    is_active=True,
                )
                .order_by("-version")
                .first()
            )
            prompt_info = (
                f" (Prompt v{prompt.version})" if prompt else " (No prompt found)"
            )
            return False, str(e), prompt_info
