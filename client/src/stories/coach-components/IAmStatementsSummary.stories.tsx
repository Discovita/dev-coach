import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from 'storybook/test';
import { http, HttpResponse } from 'msw';
import { IAmStatementsSummaryComponent } from '@/pages/chat/components/coach-message-with-component/IAmStatementsSummaryComponent';
import { ComponentType } from '@/enums/componentType';
import { IdentityCategory } from '@/enums/identityCategory';
import type { ComponentIdentity } from '@/types/componentConfig';
import { COACH_BASE_URL } from '@/constants/api';

const meta = {
  title: 'Chat/IAmStatementsSummary',
  component: IAmStatementsSummaryComponent,
  decorators: [
    (Story) => (
      <div className="p-8 bg-gray-50 dark:bg-gray-900 mx-auto w-full">
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: 'padded',
    msw: {
      handlers: [
        // Mock PDF download endpoint
        http.get(`${COACH_BASE_URL}/identities/download-i-am-statements-pdf`, async () => {
          // Return a mock PDF blob
          const pdfContent = '%PDF-1.4 mock pdf content';
          const encoder = new TextEncoder();
          const pdfBytes = encoder.encode(pdfContent);
          return HttpResponse.arrayBuffer(pdfBytes.buffer, {
            headers: {
              'Content-Type': 'application/pdf',
              'Content-Disposition': 'attachment; filename="i-am-statements.pdf"',
            },
          });
        }),
      ],
    },
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
    testUserId: {
      control: 'text',
      description: 'Optional user ID for test scenarios (uses admin endpoint)',
    },
  },
  args: {
    onSendUserMessageToCoach: fn(),
    disabled: false,
  },
} satisfies Meta<typeof IAmStatementsSummaryComponent>;

export default meta;
type Story = StoryObj<typeof meta>;

// Mock identities with I Am statements
const mockIdentity1: ComponentIdentity = {
  id: 'identity-1',
  name: 'Creative Visionary',
  category: IdentityCategory.PASSIONS_AND_TALENTS,
  i_am_statement: 'I am a bold creator, transforming ideas into reality with passion and purpose.',
};

const mockIdentity2: ComponentIdentity = {
  id: 'identity-2',
  name: 'Warrior',
  category: IdentityCategory.PHYSICAL_EXPRESSION,
  i_am_statement: 'I treat my body with strength, discipline, and respect.',
};

const mockIdentity3: ComponentIdentity = {
  id: 'identity-3',
  name: 'Loving Partner',
  category: IdentityCategory.ROMANTIC_RELATION,
  i_am_statement: 'I am a supportive and caring partner who brings joy and connection to my relationships.',
};

const mockIdentity4: ComponentIdentity = {
  id: 'identity-4',
  name: 'Successful Entrepreneur',
  category: IdentityCategory.MAKER_OF_MONEY,
  i_am_statement: 'I am a strategic business leader who creates value and builds sustainable enterprises.',
};

const mockIdentity5: ComponentIdentity = {
  id: 'identity-5',
  name: 'Spiritual Seeker',
  category: IdentityCategory.SPIRITUAL,
  i_am_statement: 'I am connected to something greater than myself, finding peace and purpose in my spiritual journey.',
};

const mockIdentity6: ComponentIdentity = {
  id: 'identity-6',
  name: 'Family Anchor',
  category: IdentityCategory.FAMILIAL_RELATIONS,
  i_am_statement: 'I am a stable and loving presence for my family, providing support and creating lasting memories.',
};

// Default story with multiple identities
export const Default: Story = {
  args: {
    coachMessage: 'Look at everything you are! This is all of the stuff that you are in one place. You should feel proud of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1, mockIdentity2, mockIdentity3, mockIdentity4],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with many identities (6)
export const ManyIdentities: Story = {
  args: {
    coachMessage: 'Look at everything you are! This is all of the stuff that you are in one place. You should feel proud of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1, mockIdentity2, mockIdentity3, mockIdentity4, mockIdentity5, mockIdentity6],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with single identity
export const SingleIdentity: Story = {
  args: {
    coachMessage: 'Look at everything you are! This is all of the stuff that you are in one place. You should feel proud of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
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
    coachMessage: 'Look at everything you are! This is all of the stuff that you are in one place. You should feel proud of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1, mockIdentity2, mockIdentity3],
    },
  },
};

// Story with different identity categories
export const DifferentCategories: Story = {
  args: {
    coachMessage: 'Look at everything you are! This is all of the stuff that you are in one place. You should feel proud of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity5, mockIdentity3, mockIdentity4],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with disabled buttons
export const Disabled: Story = {
  args: {
    coachMessage: 'Look at everything you are! This is all of the stuff that you are in one place. You should feel proud of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1, mockIdentity2, mockIdentity3],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
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
    coachMessage: 'Look at **everything** you are! This is all of the stuff that you are in one place.\n\nYou should feel **proud** of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1, mockIdentity2, mockIdentity3],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
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
        <p className="font-bold text-lg mb-2">Congratulations!</p>
        <p>Look at everything you are! This is all of the stuff that you are in one place.</p>
        <p className="mt-2">You should feel proud of yourself for having accomplished this much.</p>
      </div>
    ),
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1, mockIdentity2, mockIdentity3],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
              },
            },
          ],
        },
      ],
    },
  },
};

// Story with downloading state - MSW handler will delay the response
export const Downloading: Story = {
  args: {
    coachMessage: 'Look at everything you are! This is all of the stuff that you are in one place. You should feel proud of yourself for having accomplished this much.',
    config: {
      component_type: ComponentType.I_AM_STATEMENTS_SUMMARY,
      identities: [mockIdentity1, mockIdentity2, mockIdentity3],
      buttons: [
        {
          label: 'Continue',
          actions: [
            {
              action: 'persist_i_am_statements_summary_component',
              params: {
                coach_message_id: 'msg-1',
              },
            },
          ],
        },
      ],
    },
  },
  parameters: {
    msw: {
      handlers: [
        // Mock PDF download endpoint with delay to show loading state
        http.get(`${COACH_BASE_URL}/identities/download-i-am-statements-pdf`, async () => {
          // Simulate slow download
          await new Promise((resolve) => setTimeout(resolve, 2000));
          return HttpResponse.arrayBuffer(new ArrayBuffer(0), {
            headers: {
              'Content-Type': 'application/pdf',
              'Content-Disposition': 'attachment; filename="i-am-statements.pdf"',
            },
          });
        }),
      ],
    },
  },
};
