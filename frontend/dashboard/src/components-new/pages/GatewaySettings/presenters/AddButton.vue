<template>
  <AsyncFunctionButton
    id="add-gateway"
    :on-click-async="onClickAsync"
    :disabled="disabled"
    class="flex items-center justify-center text-ms bg-blue-500 text-white py-2 px-4 mr-2 rounded hover:bg-blue-600 w-64 ml-10"
  >
    <div class="flex">
      <RightArrowIcon />
      <span class="ml-2 font-bold">追加する</span>
    </div>
  </AsyncFunctionButton>
</template>

<script setup lang="ts">
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
import RightArrowIcon from '@icons/RightArrowIcon.vue';
defineProps<{
  onClickAsync: () => Promise<void>;
  disabled?: boolean;
}>();
</script>
