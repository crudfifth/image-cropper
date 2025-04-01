<template>
  <div class="hover:cursor-pointer">
    <div
      v-if="!isSelected"
      class="bg-light-sky text-black border-2 border-main-blue border-b-0 rounded-t-md h-[40px] w-[120px] py-1 px-2 flex justify-center items-center"
    >
      <slot name="icon"></slot>
      <span class="ml-2">{{ text }}</span>
    </div>
    <div
      v-else
      class="bg-main-blue text-white border-2 border-main-blue border-t-4 border-t-pink-500 border-b-0 rounded-t-md h-[40px] w-[120px] py-1 px-2 flex justify-center items-center"
    >
      <slot name="icon" color="text-white"></slot>
      <span class="ml-2">{{ text }}</span>
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps({
  isSelected: {
    type: Boolean,
    default: false,
  },
  text: {
    type: String,
    required: true,
  },
});
</script>
