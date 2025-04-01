<template>
  <div class="flex items-center gap-4">
    <div
      v-if="graphStateStore.timePeriod !== 'four-hour'"
      class="flex items-center gap-2"
    >
      <div
        class="relative w-3.5 h-3.5 bg-main-blue rounded-full flex items-center justify-center before:content-bar before:absolute before:w-6 before:h-1 before:bg-main-blue before:rounded-sm"
      ></div>
      <span class="text-xs font-bold">{{ previousPeriodLabel }}</span>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-4 h-4 bg-top-color rounded-sm"></div>
      <span class="text-xs font-bold">{{ currentPeriodLabel }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { graphStateStore } from '@/stores/TrendGraphStore';

const labels = {
  'four-hour': { previous: '', current: '当日' },
  day: { previous: '前日', current: '当日' },
  week: { previous: '前週', current: '今週' },
  month: { previous: '前月', current: '今月' },
  year: { previous: '昨年', current: '今年' },
};

const previousPeriodLabel = computed(
  () => labels[graphStateStore.timePeriod].previous
);
const currentPeriodLabel = computed(
  () => labels[graphStateStore.timePeriod].current
);
</script>
