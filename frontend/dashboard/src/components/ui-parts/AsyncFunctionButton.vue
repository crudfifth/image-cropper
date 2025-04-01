<!-- 
  イベントハンドラの非同期関数の実行中はクリックできない(つまり、連打できない)ボタン
-->
<template>
  <button :disabled="props.disabled || isProcessing" @click="handleClick">
    <slot>Click Me</slot>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 非同期関数を受け取るpropsの定義
const props = defineProps<{
  onClickAsync: () => Promise<void>;
  disabled?: boolean;
}>();

const isProcessing = ref(false);

const handleClick = async () => {
  if (props.onClickAsync) {
    isProcessing.value = true;
    try {
      await props.onClickAsync();
    } finally {
      isProcessing.value = false;
    }
  }
};
</script>
