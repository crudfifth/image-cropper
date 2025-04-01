<template>
  <AsyncFunctionButton
    id="submit"
    :on-click-async="onClickAsyncWrap"
    class="flex items-center justify-center text-white bg-blue-500 hover:bg-blue-600 py-2 px-4 mr-2 rounded transition duration-300 font-bold"
    :class="{
      'bg-slate-300 hover:bg-slate-300 cursor-default': disabled || uploading,
    }"
  >
    <span v-if="uploading">アップロード中...</span>
    <span v-else>アップロード</span>
  </AsyncFunctionButton>
</template>

<script setup lang="ts">
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
import { ref } from 'vue';
const props = defineProps<{
  onClickAsync: () => Promise<void>;
  disabled?: boolean;
}>();

const uploading = ref(false);

const onClickAsyncWrap = async () => {
  if (props.disabled) {
    return;
  }
  uploading.value = true;
  const result = await props.onClickAsync();
  uploading.value = false;
  return result;
};
</script>
