<template>
  <AsyncFunctionButton
    id="submit"
    :on-click-async="onClickAsync"
    :disabled="props.disabled"
    class="flex items-center justify-center text-white bg-blue-500 hover:bg-blue-600 py-2 px-4 mr-2 rounded transition duration-300 font-bold"
  >
    <UpdateIcon />
    更新する
  </AsyncFunctionButton>
</template>

<script setup lang="ts">
import AsyncFunctionButton from '@/components/ui-parts/AsyncFunctionButton.vue';
import UpdateIcon from '@icons/UpdateIcon.vue';
const props = defineProps<{
  onClickAsync: () => Promise<void>;
  disabled?: boolean;
}>();
</script>
