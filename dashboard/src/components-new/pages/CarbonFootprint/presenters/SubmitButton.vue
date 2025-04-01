<template>
  <AsyncFunctionButton
    id="submit"
    :on-click-async="onClickAsyncWrap"
    class="flex items-center justify-center text-white bg-blue-500 hover:bg-blue-600 py-2 px-4 mr-2 rounded transition duration-300 font-bold"
    :class="{ 'bg-slate-300 hover:bg-slate-300 cursor-default': disabled }"
  >
    <UpdateIcon class="w-4 h-4 mr-2" />
    <span>更新する</span>
  </AsyncFunctionButton>
</template>

<script setup lang="ts">
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
import UpdateIcon from '@icons/UpdateIcon.vue';
const props = defineProps<{
  onClickAsync: () => Promise<void>;
  disabled?: boolean;
}>();

const onClickAsyncWrap = async () => {
  if (props.disabled) {
    return;
  }
  return props.onClickAsync();
};
</script>
