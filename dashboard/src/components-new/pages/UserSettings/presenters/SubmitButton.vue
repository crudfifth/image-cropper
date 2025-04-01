<template>
  <AsyncFunctionButton
    id="submit"
    :on-click-async="onClickAsyncWrap"
    class="flex items-center justify-center text-white bg-blue-500 hover:bg-blue-600 py-2 px-4 mr-2 rounded transition duration-300 font-bold"
    :class="{ 'bg-slate-300 hover:bg-slate-300 cursor-default': disabled }"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="21.004"
      height="21.006"
      viewBox="0 0 21.004 21.006"
      class="w-5 h-5 inline mr-3 mb-1"
    >
      <g id="refresh_2_fill" transform="translate(6.502 24.503)">
        <path
          id="Path_50845"
          data-name="Path 50845"
          d="M1.5,12.082a1.6,1.6,0,0,1,2.379-1.406l.113.07,2.678,1.8a1.6,1.6,0,0,1-1.1,2.915l-.137-.025-.109-.024a7.5,7.5,0,0,0,13.175.335,1.5,1.5,0,1,1,2.6,1.5A10.5,10.5,0,0,1,1.5,12.082ZM2.9,6.752a10.5,10.5,0,0,1,19.6,5.165,1.6,1.6,0,0,1-2.379,1.407l-.113-.07-2.678-1.805a1.6,1.6,0,0,1,1.1-2.914l.138.025.108.023A7.5,7.5,0,0,0,5.5,8.25a1.5,1.5,0,1,1-2.6-1.5Z"
          transform="translate(-8 -26)"
          fill="#fff"
        />
      </g>
    </svg>
    {{ buttonText }}
  </AsyncFunctionButton>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
const props = defineProps<{
  onClickAsync: () => Promise<void>;
  disabled?: boolean;
  isAdding?: boolean;
}>();

const buttonText = computed(() => props.isAdding ? '登録' : '更新する');

const onClickAsyncWrap = async () => {
  if (props.disabled) {
    return;
  }
  return props.onClickAsync();
};
</script>
