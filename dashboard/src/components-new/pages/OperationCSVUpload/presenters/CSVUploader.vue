<template>
  <div
    class="p-8 border-red-400 border-2 rounded-lg"
    :class="{ 'bg-blue-100': isHovering }"
    @dragover.prevent="handleDragOver"
    @drop.prevent="handleFileUpload"
    @dragleave.prevent="handleDragLeave"
  >
    <div class="flex justify-center items-center">
      <input
        ref="fileInput"
        type="file"
        accept=".csv"
        hidden
        @change="handleFileUpload"
      />
      <button
        class="mr-2 text-sm bg-white hover:bg-blue-500 hover:text-white py-2 px-4 border-2 hover:border-transparent rounded"
        @click="triggerFileInput"
      >
        ファイルを選択
      </button>
      <div v-if="fileName">{{ fileName }}</div>
    </div>
    <div class="text-center text-sm mt-2">
      ※ドラッグ＆ドロップでもアップロード可能です
    </div>
  </div>
</template>

<script lang="ts" setup>
import { openAlertModal } from '@/stores/AlertModalStore';
import { ref } from 'vue';

type Emits = {
  (event: 'upload', { content, name }: { content: string; name: string }): void;
};

const emit = defineEmits<Emits>();
defineProps<{
  fileName: string;
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const isHovering = ref(false);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileUpload = (event: Event) => {
  isHovering.value = false;
  const files =
    (event as DragEvent).dataTransfer?.files ||
    (event.target as HTMLInputElement).files;
  if (!files || files.length === 0) {
    return;
  }
  const file = files[0];
  if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
    openAlertModal({ body: 'CSVファイルのみ受け付け可能です' });
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    const content = reader.result as string;
    emit('upload', { content, name: file.name });
  };
  reader.onerror = () => {
    openAlertModal({ body: 'ファイルの読み込みに失敗しました' });
  };
  reader.readAsText(file);
};

const handleDragOver = () => {
  isHovering.value = true;
};

const handleDragLeave = () => {
  isHovering.value = false;
};
</script>
