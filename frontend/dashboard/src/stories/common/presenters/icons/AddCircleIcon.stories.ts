import AddCircleIcon from '@/components/icons/AddCircleIcon.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

type Story = StoryObj<typeof AddCircleIcon>;

const meta: Meta<typeof AddCircleIcon> = {
  title: 'Common/Presenters/Icons/AddCircleIcon',
  component: AddCircleIcon,
};

export default meta;

export const Default: Story = {
  render: () => ({
    components: { AddCircleIcon },
    template: '<AddCircleIcon color="red" />',
  }),
};


