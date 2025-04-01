<template>
  <h2 class="text-xl font-bold mb-4">稼働CSVデータアップロード</h2>
  <div class="flex justify-center items-center w-full">
    <CsvFormatAndManual class="mr-10" />
    <div class="w-1/2">
      <CSVUploader :file-name="fileName" @upload="handleCSVUpload" />
      <div class="flex justify-center mt-8">
        <SubmitButton :on-click-async="submitCSV" :disabled="emptyCsvContent" />
      </div>
    </div>
  </div>
  <h2 class="text-xl font-bold mb-4 mt-4">アップロード履歴</h2>
  <div class="flex justify-center">
    <CSVUploadHistoryList :history-list="historyList" />
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import CSVUploader from '../presenters/CSVUploader.vue';
import CSVUploadHistoryList, {
  History,
} from '../presenters/CSVUploadHistoryList.vue';
import SubmitButton from '../presenters/SubmitButton.vue';
import CsvFormatAndManual from '../presenters/CsvFormatAndManual.vue';
import CsvService from '@/services/CsvService';

import { computed } from 'vue';

const csvContent = ref('');
const fileName = ref('');
const historyList = ref<History[]>([]);

onMounted(async () => {
  historyList.value = await CsvService.fetchCsvUploadHistories();
});

const handleCSVUpload = ({
  content,
  name,
}: {
  content: string;
  name: string;
}) => {
  csvContent.value = content;
  fileName.value = name;
};

const emptyCsvContent = computed(() => csvContent.value === '');

const submitCSV = async () => {
  await CsvService.uploadCsv(csvContent.value, fileName.value);
  csvContent.value = '';
  fileName.value = '';
  historyList.value = await CsvService.fetchCsvUploadHistories();
};
</script>
