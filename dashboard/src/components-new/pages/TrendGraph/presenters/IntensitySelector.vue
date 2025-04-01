<template>
  <div class="flex justify-between gap-2 border bg-gray-50 rounded px-2 py-1">
    <label class="cursor-pointer text-center">
      <input
        v-model="localValue"
        type="radio"
        name="radio-unit"
        class="peer sr-only"
        value="default"
        checked
      />
      <div
        class="text-zinc-300 peer-checked:text-main-blue peer-checked:bg-white drop-shadow-md rounded px-2 py-1 whitespace-nowrap"
        aria-hidden="true"
      >
        標準
      </div>
    </label>
    <label class="cursor-pointer text-center">
      <input
        v-model="localValue"
        type="radio"
        name="radio-unit"
        class="peer sr-only"
        value="intensity"
        :disabled="intensityDisabled"
      />
      <div
        class="text-zinc-300 peer-checked:text-main-blue peer-checked:bg-white drop-shadow-md rounded px-2 py-1 whitespace-nowrap"
        aria-hidden="true"
      >
        原単位
      </div>
    </label>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import { IntensityType } from '@/types';
import { graphStateStore } from '@/stores/TrendGraphStore';

const intensityDisabled = computed(() => !graphStateStore.unitSettingAvailable);

watch(intensityDisabled, () => {
  if (intensityDisabled.value && graphStateStore.intensity === 'intensity') {
    graphStateStore.intensity = 'default';
  }
});

// TODO: Storeへの依存を切り離す(コンテナコンポーネントで管理する)
const localValue = computed({
  get: () => graphStateStore.intensity,
  set: (value: IntensityType) => {
    graphStateStore.intensity = value;
  },
});
</script>
