<!-- 
  イベントハンドラの非同期関数の実行中はクリックできない(つまり、連打できない)ボタン
-->
<template>
  <button
    :disabled="isProcessing || props.disabled"
    :class="{
      'bg-gray-400': props.disabled,
      'hover:bg-gray-400': props.disabled,
    }"
    type="button"
    @click="handleClick"
  >
    <!-- TODO:スピナーをあとで外出しする -->
    <span class="spinner" :class="isProcessing ? 'absolute' : 'hidden'"></span>
    <div :class="isProcessing ? 'collapse' : 'visible'">
      <slot>Click Me</slot>
    </div>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  onClickAsync?: () => Promise<void>;
  disabled?: boolean;
}>();

const isProcessing = ref(false);

const handleClick = async () => {
  if (props.onClickAsync && !props.disabled) {
    isProcessing.value = true;
    try {
      await props.onClickAsync();
    } finally {
      isProcessing.value = false;
    }
  }
};
</script>

<style scoped>
.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 4px solid #fff;
  width: 16px;
  height: 16px;
  -webkit-animation: spin 1s linear infinite;
  animation: spin 1s linear infinite;
}

/* .bg-gray-500 {
  background-color: #6b7280; 
} */

@-webkit-keyframes spin {
  0% {
    -webkit-transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
