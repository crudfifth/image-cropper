<template>
  <table class="table-auto border-spacing-1 border-separate text-sm">
    <thead>
      <tr>
        <th class="py-1 px-2 bg-stone-200">ファイル名</th>
        <th class="py-1 px-2 bg-stone-200">容量</th>
        <th class="py-1 px-2 bg-stone-200">更新日時</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="history in historyList" :key="history.id">
        <td class="py-1 px-2">{{ history.fileName }}</td>
        <td class="py-1 px-2">{{ formatFileSize(history.size) }}</td>
        <td class="py-1 px-2">{{ history.date.toLocaleString() }}</td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
export type History = {
  id: string;
  fileName: string;
  size: number;
  date: Date;
};

defineProps<{
  historyList: History[];
}>();

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return (
    Math.floor(parseFloat((bytes / Math.pow(k, i)).toFixed(2))) + ' ' + sizes[i]
  );
};
</script>
