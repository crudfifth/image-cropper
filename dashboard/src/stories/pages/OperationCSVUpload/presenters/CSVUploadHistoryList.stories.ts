import CSVUploadHistoryList from '@/components-new/pages/OperationCSVUpload/presenters/CSVUploadHistoryList.vue';
import { Meta, StoryObj } from '@storybook/vue3';

type Story = StoryObj<typeof CSVUploadHistoryList>;

const meta: Meta<typeof CSVUploadHistoryList> = {
  title: 'Pages/OperationCSVUpload/Presenters/CSVUploadHistoryList',
  component: CSVUploadHistoryList,
};

export default meta;

export const Default: Story = {
  render: (args) => {
    return {
      components: { CSVUploadHistoryList },
      setup() {
        return { args };
      },
      template: `
        <CSVUploadHistoryList v-bind="args" />
      `,
    };
  },
  args: {
    historyList: [
      {
        id: '1',
        fileName: 'sample.csv',
        size: 1024,
        date: new Date(),
      },
      {
        id: '2',
        fileName: 'sample2.csv',
        size: 1000,
        date: new Date(),
      },
      {
        id: '3',
        fileName: 'sample3.csv',
        size: 4194304,
        date: new Date(),
      },
    ],
  },
};
