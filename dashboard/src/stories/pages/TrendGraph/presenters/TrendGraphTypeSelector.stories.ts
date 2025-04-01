import TrendGraphTypeSelector from '@/components-new/pages/TrendGraph/presenters/TrendGraphTypeSelector.vue';
import { useArgs } from '@storybook/preview-api';
import { Meta, StoryObj } from '@storybook/vue3';
import type { TrendGraphType } from '@/types';

type Story = StoryObj<typeof TrendGraphTypeSelector>;

const meta: Meta<typeof TrendGraphTypeSelector> = {
  title: 'Pages/TrendGraph/Presenters/TrendGraphTypeSelector',
  component: TrendGraphTypeSelector,
};

export default meta;

export const Default: Story = {
  args: {
    modelValue: 'electricity',
  },
  argTypes: {
    modelValue: { control: 'text' },
  },
  render: (args) => {
    const [, updateArgs] = useArgs<typeof args>();
    return {
      components: { TrendGraphTypeSelector },
      setup: () => {
        const handlers: (typeof TrendGraphTypeSelector)['emits'] = {
          'update:modelValue': ($event: TrendGraphType) =>
            updateArgs({ modelValue: $event }),
        };
        return {
          args,
          handlers,
        };
      },
      template: `
        <TrendGraphTypeSelector v-bind="args" v-on="handlers"/>
      `,
    };
  },
};
