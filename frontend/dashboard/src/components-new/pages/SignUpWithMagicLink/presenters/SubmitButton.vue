<template>
  <AsyncFunctionButton
    class="flex items-center justify-center px-4 rounded bg-blue-500 hover:bg-blue-600 text-white py-2 font-bold"
    :on-click-async="isDisabled ? emptyAction : onClickAsync"
    :disabled="isDisabled"
  >
    登録
  </AsyncFunctionButton>
</template>

<script setup lang="ts">
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';

const emptyAction = () => Promise.resolve();

defineProps<{
  onClickAsync: () => Promise<void>;
  isDisabled?: boolean;
}>();
</script>
