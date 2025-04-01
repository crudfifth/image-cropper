<!-- メインエリアヘッダ -->
<template>
  <div class="flex flex-col 2xl:flex-row justify-between gap-2 pb-4">
    <h2 class="text-2xl font-bold whitespace-nowrap">
      <GraphIcon class="w-6 h-6 inline" color="text-main-blue" />
      トレンドグラフ
    </h2>

    <TrendGraphLegend />

    <div class="flex justify-between items-center gap-2">
      <TimePeriodSelector />
      <DayTimeSelector v-model="startDateTime" />
      <IntensitySelector />
      <TrendGraphTypeSelector v-model="graphType" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import GraphIcon from '../../../common/presenters/icons/GraphIcon.vue';
import TimePeriodSelector from '../presenters/TimePeriodSelector.vue';
import DayTimeSelector from '../presenters/DayTimeSelector.vue';
import IntensitySelector from '../presenters/IntensitySelector.vue';
import TrendGraphTypeSelector from '../presenters/TrendGraphTypeSelector.vue';
import TrendGraphLegend from '../presenters/TrendGraphLegend.vue';
import type { TimePeriodType, IntensityType, TrendGraphType } from '@/types';
import type { GraphKeyType } from '@/services/GraphService';

import { graphStateStore } from '@/stores/TrendGraphStore';

import { ref, watch } from 'vue';

const graphType = computed({
  get: () => graphStateStore.graphType,
  set: (value: TrendGraphType) => (graphStateStore.graphType = value),
});
const startDateTime = computed<Date>({
  get: () => graphStateStore.startDates[graphStateStore.timePeriod],
  set: (value: Date) =>
    (graphStateStore.startDates[graphStateStore.timePeriod] =
      value ?? new Date()),
});

// type PropsType = {
//   timePeriod: TimePeriodType;
//   date: Date;
//   intensity: IntensityType;
//   graphType: TrendGraphType;
//   selectedGraphs: GraphKeyType[];
// };

// type ModelType<T> = {
//   modelValue: T;
// };

//const props = defineProps<ModelType<PropsType>>();

//const emit = defineEmits(['update:modelValue']);

// const selectedTimePeriod = ref<TimePeriodType>(props.modelValue.timePeriod);
// const selectedDate = ref<Date>(props.modelValue.date);
// const selectedIntensity = ref<IntensityType>(props.modelValue.intensity);
// const selectedGraphType = ref<TrendGraphType>(props.modelValue.graphType);

// watch(
//   [selectedTimePeriod, selectedDate, selectedIntensity, selectedGraphType],
//   () => {
//     emit('update:modelValue', {
//       timePeriod: selectedTimePeriod.value,
//       date: selectedDate.value,
//       intensity: selectedIntensity.value,
//       graphType: selectedGraphType.value,
//       selectedGraphs: props.modelValue.selectedGraphs,
//     });
//   }
// );
</script>
