import CSVUploader from '@/components-new/pages/OperationCSVUpload/presenters/CSVUploader.vue';
import { Meta, StoryObj } from '@storybook/vue3';

type Story = StoryObj<typeof CSVUploader>;

const meta: Meta<typeof CSVUploader> = {
  title: 'Pages/OperationCSVUpload/Presenters/CSVUploader',
  component: CSVUploader,
};

export default meta;

export const Default: Story = {
  render: (args) => {
    return {
      components: { CSVUploader },
      setup() {
        return { args };
      },
      template: `
        <CSVUploader v-bind="args" />
      `,
    };
  },
  argTypes: {
    onUpload: { action: 'onUpload' },
  },
};
