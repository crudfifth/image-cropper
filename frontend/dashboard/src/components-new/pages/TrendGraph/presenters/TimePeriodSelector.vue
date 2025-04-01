<template>
  <div class="flex justify-between items-center gap-2">
    <div class="flex justify-between gap-2 border bg-gray-50 rounded px-2 py-1">
      <label
        v-for="[type, label] in Array.from(labels)"
        :key="type"
        class="cursor-pointer text-center"
      >
        <input
          v-model="localValue"
          type="radio"
          name="radio-range"
          class="peer sr-only"
          :value="type"
        />
        <div
          class="text-zinc-300 peer-checked:text-main-blue peer-checked:bg-white drop-shadow-md rounded px-2 py-1"
          aria-hidden="true"
        >
          {{ label }}
        </div>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TimePeriodType } from '@/types';
import { graphStateStore } from '@/stores/TrendGraphStore';

const labels = new Map<TimePeriodType, string>([
  ['four-hour', '分'],
  ['day', '日'],
  ['week', '週'],
  ['month', '月'],
]);
// TODO: Storeへの依存を切り離す(コンテナコンポーネントで管理する)
const localValue = computed({
  get: () => graphStateStore.timePeriod,
  set: (value: TimePeriodType) => (graphStateStore.timePeriod = value),
});
</script>
