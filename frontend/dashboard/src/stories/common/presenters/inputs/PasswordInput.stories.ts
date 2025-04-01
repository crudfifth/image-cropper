import PasswordInput from '@/components-new/common/presenters/inputs/PasswordInput.vue';
import { useArgs } from '@storybook/preview-api';
import type { Meta, StoryObj } from '@storybook/vue3';

type Story = StoryObj<typeof PasswordInput>;

const meta: Meta<typeof PasswordInput> = {
  title: 'Common/Presenters/Inputs/PasswordInput',
  component: PasswordInput,
};

export default meta;

export const Default: Story = {
  args: {
    modelValue: '',
  },
  argTypes: {
    modelValue: { control: 'text' },
    placeholder: { control: 'text' },
  },
  render: (args) => {
    const [, updateArgs] = useArgs<typeof args>();
    return {
      components: { PasswordInput },
      setup: () => {
        const handlers: (typeof PasswordInput)['emits'] = {
          'update:modelValue': ($event: string) =>
            updateArgs({ modelValue: $event }),
        };
        return {
          args,
          handlers,
        };
      },
      template: `
      <div class="w-48">
        <PasswordInput
          v-bind="args"
          v-on="handlers"
        />
      </div>
    `,
    };
  },
};
