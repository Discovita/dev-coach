import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from 'storybook/test';
import { NestIdentitiesConfirmation } from './NestIdentitiesConfirmation';
import { ComponentType } from '@/enums/componentType';
import { IdentityCategory } from '@/enums/identityCategory';

const meta = {
  title: 'Chat/NestIdentitiesConfirmation',
  component: NestIdentitiesConfirmation,
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
} satisfies Meta<typeof NestIdentitiesConfirmation>;

export default meta;
type Story = StoryObj<typeof meta>;

// Mock identities for different scenarios
const mockParentIdentity = {
  id: 'parent-1',
  name: 'Successful Entrepreneur',
  category: IdentityCategory.MAKER_OF_MONEY,
};

const mockNestedIdentity = {
  id: 'nested-1',
  name: 'Business Owner',
  category: IdentityCategory.DOER_OF_THINGS,
};

const mockParentIdentitySpiritual = {
  id: 'parent-2',
  name: 'Spiritual Seeker',
  category: IdentityCategory.SPIRITUAL,
};

const mockNestedIdentityRomantic = {
  id: 'nested-2',
  name: 'Loving Partner',
  category: IdentityCategory.ROMANTIC_RELATION,
};

// Default story with buttons
export const Default: Story = {
  args: {
    coachMessage: 'I notice you have two identities that could be nested together. Would you like to nest **Business Owner** under **Successful Entrepreneur**?',
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [mockNestedIdentity, mockParentIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'nest_identities',
              params: {
                nested_identity_id: mockNestedIdentity.id,
                parent_identity_id: mockParentIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [],
        },
      ],
    },
  },
};

// Story without buttons
export const WithoutButtons: Story = {
  args: {
    coachMessage: 'I notice you have two identities that could be nested together. Would you like to nest **Business Owner** under **Successful Entrepreneur**?',
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [mockNestedIdentity, mockParentIdentity],
    },
  },
};

// Story with different identity categories
export const DifferentCategories: Story = {
  args: {
    coachMessage: 'Would you like to nest **Loving Partner** under **Spiritual Seeker**?',
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [mockNestedIdentityRomantic, mockParentIdentitySpiritual],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'nest_identities',
              params: {
                nested_identity_id: mockNestedIdentityRomantic.id,
                parent_identity_id: mockParentIdentitySpiritual.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [],
        },
      ],
    },
  },
};

// Story with loading state (null identities)
export const LoadingState: Story = {
  args: {
    coachMessage: 'Loading identities...',
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [null, null] as unknown as typeof mockNestedIdentity[],
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

// Story with partial loading (one identity loaded)
export const PartialLoading: Story = {
  args: {
    coachMessage: 'Loading the second identity...',
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [mockNestedIdentity, null] as unknown as typeof mockNestedIdentity[],
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
    coachMessage: 'I notice you have two identities that could be nested together. Would you like to nest **Business Owner** under **Successful Entrepreneur**?',
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [mockNestedIdentity, mockParentIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'nest_identities',
              params: {
                nested_identity_id: mockNestedIdentity.id,
                parent_identity_id: mockParentIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [],
        },
      ],
    },
    disabled: true,
  },
};

// Story with markdown in coach message
export const WithMarkdown: Story = {
  args: {
    coachMessage: 'I notice you have **two identities** that could be nested together:\n\n- Business Owner\n- Successful Entrepreneur\n\nWould you like to nest them?',
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [mockNestedIdentity, mockParentIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'nest_identities',
              params: {
                nested_identity_id: mockNestedIdentity.id,
                parent_identity_id: mockParentIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [],
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
        <p>Would you like to nest these identities?</p>
      </div>
    ),
    config: {
      component_type: ComponentType.NEST_IDENTITIES,
      identities: [mockNestedIdentity, mockParentIdentity],
      buttons: [
        {
          label: 'Yes',
          actions: [
            {
              action: 'nest_identities',
              params: {
                nested_identity_id: mockNestedIdentity.id,
                parent_identity_id: mockParentIdentity.id,
              },
            },
          ],
        },
        {
          label: 'No',
          actions: [],
        },
      ],
    },
  },
};

