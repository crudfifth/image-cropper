<template>
  <AsyncFunctionButton
    id="add-carbon-footprint"
    :on-click-async="onClickAsyncWrap"
    class="px-4 rounded bg-green-600 hover:bg-green-700 text-white py-2 font-bold"
    :class="{ 'bg-slate-300 hover:bg-slate-300 cursor-default': disabled }"
  >
    <div class="flex items-center">
      <AddCircleIcon class="mr-2" />
      <span>新規追加</span>
    </div>
  </AsyncFunctionButton>
</template>

<script setup lang="ts">
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
import AddCircleIcon from '@icons/AddCircleIcon.vue';

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
