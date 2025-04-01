<template>
  <div
    class="flex justify-between text-slate-700 bg-sky-50 rounded-md border-3"
    :class="improvementRate >= 0 ? 'border-green-500' : 'border-red-500'"
  >
    <span
      class="text-white text-lg py-1 px-4 font-bold"
      :class="improvementRate >= 0 ? 'bg-green-500' : 'bg-red-500'"
    >
      {{ improvementRate >= 0 ? '改善' : '悪化' }}
    </span>
    <div class="pr-4">
      <span class="text-2xl font-bold">{{ Math.abs(improvementRate) }}</span>
      <span class="text-ms">%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  improvementRate: number;
}>();
</script>
