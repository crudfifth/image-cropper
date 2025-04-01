<template>
  <div
    class="bg-light-sky rounded-md inline-block px-[24px] pt-[20px] pb-[16px]"
  >
    <div class="flex justify-between items-center">
      <div class="text-2xl font-bold">{{ period }}</div>
      <div class="text-[14px]">昨年実績：{{ prevYearAchievement }}</div>
    </div>
    <div class="flex justify-between items-center">
      <div class="text-[18px] font-bold">目標</div>
      <div class="flex items-center">
        <input
          v-model="inputValue"
          name="target"
          class="hide-spin outline-none p-[8px] text-[14px] text-right placeholder-gray-400 rounded-md w-[174px] h-[40px] mx-[16px]"
          :class="{
            'border-2 border-red-500': !isValid,
          }"
          placeholder="入力してください"
          @input="$emit('input-target', inputValue)"
        /><span class="text-[18px] font-bold">{{ unit }}</span>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Ref, computed, ref } from 'vue';
const props = defineProps({
  period: {
    type: String,
    required: true,
  },
  prevYearAchievement: {
    type: String,
    required: true,
  },
  targetValue: {
    type: String,
    default: undefined,
  },
  unit: {
    type: String,
    required: true,
  },
});

const inputValue: Ref<number | string | undefined> = ref(props.targetValue);

const isValid = computed(() => {
  if (
    inputValue.value === '' ||
    Number(inputValue.value) < 0 ||
    isNaN(Number(inputValue.value)) ||
    String(inputValue.value).includes('.')
  ) {
    return false;
  }
  return true;
});
</script>
<style scoped lang="css">
.hide-spin::-webkit-inner-spin-button,
.hide-spin::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
