import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from 'storybook/test';
import { ArchiveIdentityConfirmation } from '@/pages/chat/components/coach-message-with-component/ArchiveIdentityConfirmation';
import { ComponentType } from '@/enums/componentType';
import { IdentityCategory } from '@/enums/identityCategory';
import type { ComponentIdentity } from '@/types/componentConfig';

const meta = {
  title: 'Chat/ArchiveIdentityConfirmation',
  component: ArchiveIdentityConfirmation,
  decorators: [
    (Story) => (
      <div className="p-8 bg-gray-50 dark:bg-gray-900 mx-auto w-full">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    disabled: {
      control: 'boolean',
      description: 'Whether the buttons are disabled',
    },
    coachMessage: {
      control: 'text',
      description: 'The coach message content (markdown supported)',
    },
  },
  args: {
    onSendUserMessageToCoach: fn(),
    disabled: false,
  },
} satisfies Meta<typeof ArchiveIdentityConfirmation>;

export default meta;
type Story = StoryObj<typeof meta>;

// Mock identities for different scenarios
const mockIdentity = {
  id: 'identity-1',
  name: 'Business Owner',
  category: IdentityCategory.MAKER_OF_MONEY,
};

const mockIdentitySpiritual = {
  id: 'identity-2',
  name: 'Spiritual Seeker',
  category: IdentityCategory.SPIRITUAL,
};

const mockIdentityRomantic = {
  id: 'identity-3',
  name: 'Loving Partner',
  category: IdentityCategory.ROMANTIC_RELATION,
};

const mockIdentityLongName = {
  id: 'identity-4',
  name: 'Very Long Identity Name That Might Overflow',
  category: IdentityCategory.DOER_OF_THINGS,
};

// Default story with buttons
export const Default: Story = {
  args: {
    coachMessage: 'I notice you have an identity that might not be needed anymore. Would you like to archive **Business Owner**?',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'persist_archive_identity',
              params: {
                identity_id: mockIdentity.id,
                coach_message_id: 'msg-1',
              },
            },
            {
              action: 'archive_identity',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [
            {
              action: 'accept_identity_commitment',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
      ],
    },
  },
};

// Story without buttons
export const WithoutButtons: Story = {
  args: {
    coachMessage: 'I notice you have an identity that might not be needed anymore. Would you like to archive **Business Owner**?',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentity],
    },
  },
};

// Story with different identity categories
export const DifferentCategories: Story = {
  args: {
    coachMessage: 'Would you like to archive **Spiritual Seeker**?',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentitySpiritual],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'persist_archive_identity',
              params: {
                identity_id: mockIdentitySpiritual.id,
                coach_message_id: 'msg-2',
              },
            },
            {
              action: 'archive_identity',
              params: {
                id: mockIdentitySpiritual.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [
            {
              action: 'accept_identity_commitment',
              params: {
                id: mockIdentitySpiritual.id,
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with romantic category
export const RomanticCategory: Story = {
  args: {
    coachMessage: 'Would you like to archive **Loving Partner**?',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentityRomantic],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'persist_archive_identity',
              params: {
                identity_id: mockIdentityRomantic.id,
                coach_message_id: 'msg-3',
              },
            },
            {
              action: 'archive_identity',
              params: {
                id: mockIdentityRomantic.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [
            {
              action: 'accept_identity_commitment',
              params: {
                id: mockIdentityRomantic.id,
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with long identity name
export const LongIdentityName: Story = {
  args: {
    coachMessage: 'Would you like to archive **Very Long Identity Name That Might Overflow**?',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentityLongName],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'persist_archive_identity',
              params: {
                identity_id: mockIdentityLongName.id,
                coach_message_id: 'msg-4',
              },
            },
            {
              action: 'archive_identity',
              params: {
                id: mockIdentityLongName.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [
            {
              action: 'accept_identity_commitment',
              params: {
                id: mockIdentityLongName.id,
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with loading state (null identity)
export const LoadingState: Story = {
  args: {
    coachMessage: 'Loading identity...',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [null] as unknown as ComponentIdentity[],
      buttons: [
        {
          label: 'Yes',
          actions: [],
        },
        {
          label: 'No',
          actions: [],
        },
      ],
    },
  },
};

// Story with disabled buttons
export const Disabled: Story = {
  args: {
    coachMessage: 'I notice you have an identity that might not be needed anymore. Would you like to archive **Business Owner**?',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'persist_archive_identity',
              params: {
                identity_id: mockIdentity.id,
                coach_message_id: 'msg-1',
              },
            },
            {
              action: 'archive_identity',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [
            {
              action: 'accept_identity_commitment',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
      ],
    },
    disabled: true,
  },
};

// Story with markdown in coach message
export const WithMarkdown: Story = {
  args: {
    coachMessage: 'I notice you have an identity that might not be needed anymore:\n\n- **Business Owner**\n\nWould you like to archive it?',
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'persist_archive_identity',
              params: {
                identity_id: mockIdentity.id,
                coach_message_id: 'msg-1',
              },
            },
            {
              action: 'archive_identity',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [
            {
              action: 'accept_identity_commitment',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with React element as coach message
export const WithReactElementMessage: Story = {
  args: {
    coachMessage: (
      <div>
        <p className="font-bold">Important:</p>
        <p>Would you like to archive this identity?</p>
      </div>
    ),
    config: {
      component_type: ComponentType.ARCHIVE_IDENTITY,
      identities: [mockIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'persist_archive_identity',
              params: {
                identity_id: mockIdentity.id,
                coach_message_id: 'msg-1',
              },
            },
            {
              action: 'archive_identity',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [
            {
              action: 'accept_identity_commitment',
              params: {
                id: mockIdentity.id,
              },
            },
          ],
        },
      ],
    },
  },
};

