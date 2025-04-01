<template>
  <h2 class="text-2xl font-bold mb-2">
    <CarbonFootprintIcon class="w-6 h-6 inline" />
    カーボンフットプリント
  </h2>
  <h3 class="text-lg mb-2">
    <span class="font-bold">取得開始日時</span>
  </h3>
  <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md mb-3">
    <div class="pr-4">
      <div class="w-full">
        <VueDatePicker
          v-model="startDate"
          :teleport="true"
          placeholder="日時を選択"
          locale="jp"
          format="yyyy年MM月dd日 HH:mm"
          select-text="OK"
          cancel-text="キャンセル"
          :clearable="false"
          :time-picker-inline="true"
          :enable-time-picker="true"
          :min-date="minDate"
          :max-date="maxDate"
        />
      </div>
    </div>
  </div>
  <h3 class="text-lg mb-2">
    <span class="font-bold">取得終了日時</span>
  </h3>
  <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md mb-3">
    <div class="pr-4">
      <div class="w-full">
        <VueDatePicker
          v-model="endDate"
          :teleport="true"
          placeholder="日時を選択"
          locale="jp"
          format="yyyy年MM月dd日 HH:mm"
          select-text="OK"
          cancel-text="キャンセル"
          :clearable="false"
          :time-picker-inline="true"
          :enable-time-picker="true"
          :min-date="minDate"
          :max-date="maxDate"
        />
      </div>
    </div>
  </div>
  <h3 class="text-lg mb-2">
    <span class="font-bold">上記期間における電力量</span>
  </h3>
  <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md mb-3">
    <div class="pr-4">
      <span class="text-2xl font-bold">{{ electricalEnergySum }}</span>
      <span class="text-ms">kWh</span>
    </div>
  </div>
  <h3 class="text-lg mb-2">
    <span class="font-bold">その期間におけるCO₂排出量</span>
  </h3>
  <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md mb-3">
    <div class="pr-4">
      <span class="text-2xl font-bold">{{ co2EmissionSum }}</span>
      <span class="text-ms">kg-CO₂</span>
    </div>
  </div>
  <div class="flex justify-center mt-7">
    <button
      id="download-csv"
      class="flex items-center gap-1 text-sm bg-blue-500 hover:bg-blue-400 hover:text-white mr-2 py-2 px-4 rounded"
      @click="commitCarbonFootprint"
    >
      保存する
    </button>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import { sumBy } from 'lodash-es';
import VueDatePicker from '@vuepic/vue-datepicker';
import CarbonFootprintIcon from '../../../common/presenters/icons/CarbonFootprintIcon.vue';
import { roundTwoDecimal } from '@/utils/Round';
import {
  carbonFootprintStore,
  graphDataStore,
  graphStateStore,
} from '@/stores/TrendGraphStore';
import CarbonFootprintService from '@/services/CarbonFootprintService';
import { cloneDeep } from 'lodash-es';

const minDate = ref(new Date());
const maxDate = ref(new Date());

const startDate = computed({
  get: () => carbonFootprintStore[graphStateStore.timePeriod].startDate,
  set: (value: Date) =>
    (carbonFootprintStore[graphStateStore.timePeriod].startDate = value),
});

const endDate = computed({
  get: () => carbonFootprintStore[graphStateStore.timePeriod].endDate,
  set: (value: Date) =>
    (carbonFootprintStore[graphStateStore.timePeriod].endDate = value),
});

watch(
  () => cloneDeep(graphStateStore.startDates),
  (newValue, oldValue) => {
    if (
      newValue[graphStateStore.timePeriod] !==
      oldValue[graphStateStore.timePeriod]
    ) {
      // 4時間の表示範囲の場合は、前に設定していた表示範囲と重なっていることがあるので特別扱いする
      if (graphStateStore.timePeriod === 'four-hour') {
        // 新しく設定したグラフの表示範囲に選択範囲が含まれている場合、選択範囲のリセットを行わない
        const fourHourRangeStart = new Date(newValue['four-hour']);
        const fourHourRangeEnd = new Date(
          fourHourRangeStart.getTime() + 4 * 60 * 60 * 1000
        );
        if (
          !(
            startDate.value >= fourHourRangeStart &&
            endDate.value <= fourHourRangeEnd
          )
        ) {
          updateDateRange();
        }
      } else {
        updateDateRange();
      }
    }
  },
  { deep: true }
);

watch(endDate, (newEndDate) => {
  if (newEndDate < startDate.value) {
    startDate.value = new Date(endDate.value);
  }
});

watch(startDate, (newStartDate) => {
  if (endDate.value < newStartDate) {
    endDate.value = new Date(newStartDate);
  }
});

const updateDateRange = () => {
  const periodStartDate =
    graphStateStore.startDates[graphStateStore.timePeriod] || new Date();
  let newStartDate, newEndDate;

  switch (graphStateStore.timePeriod) {
    case 'day':
      newStartDate = new Date(periodStartDate.setHours(0, 0, 0, 0));
      newEndDate = new Date(newStartDate);
      newEndDate.setHours(23, 59, 59, 999);
      break;
    case 'week':
      newStartDate = new Date(periodStartDate);
      newStartDate.setDate(
        newStartDate.getDate() -
          newStartDate.getDay() +
          (newStartDate.getDay() === 0 ? -6 : 1)
      );
      newStartDate.setHours(0, 0, 0, 0);
      newEndDate = new Date(newStartDate);
      newEndDate.setDate(newStartDate.getDate() + 6);
      newEndDate.setHours(23, 59, 59, 999);
      break;
    case 'month':
      newStartDate = new Date(
        periodStartDate.getFullYear(),
        periodStartDate.getMonth(),
        1
      );
      newEndDate = new Date(
        periodStartDate.getFullYear(),
        periodStartDate.getMonth() + 1,
        0
      );
      newEndDate.setHours(23, 59, 59, 999);
      break;
    case 'four-hour':
      newStartDate = new Date(periodStartDate);
      newEndDate = new Date(newStartDate.getTime() + 4 * 60 * 60 * 1000);
      break;
    default:
      newStartDate = new Date(periodStartDate);
      newEndDate = new Date(periodStartDate);
  }
  startDate.value = newStartDate;
  endDate.value = newStartDate;
  minDate.value = newStartDate;
  maxDate.value = newEndDate;
};

const electricalEnergySum = computed(() => {
  if (graphDataStore.graphData) {
    const dataPoints = Object.values(graphDataStore.graphData)
      .flatMap((graph) => graph.dataPoints)
      .map((x) => ({
        date: new Date(x.year, x.month - 1, x.date, x.hour ?? 0, x.minute ?? 0),
        value: x.electrical_value,
      }))
      .filter((x) => startDate.value <= x.date && x.date <= endDate.value);
    const sum = sumBy(dataPoints, (dataPoint) => dataPoint.value);
    return roundTwoDecimal(sum);
  }
  return 0;
});

const co2EmissionSum = computed(() => {
  if (graphDataStore.graphData) {
    const dataPoints = Object.values(graphDataStore.graphData)
      .flatMap((graph) => graph.dataPoints)
      .map((x) => ({
        date: new Date(x.year, x.month - 1, x.date, x.hour ?? 0, x.minute ?? 0),
        value: x.co2_value,
      }))
      .filter((x) => startDate.value <= x.date && x.date <= endDate.value);
    const sum = sumBy(dataPoints, (dataPoint) => dataPoint.value);
    return roundTwoDecimal(sum);
  }
  return 0;
});

const commitCarbonFootprint = async () => {
  await CarbonFootprintService.createCarbonFootprint({
    process_name: '工程1',
    channel_name: 'チャンネル1',
    start_date: startDate.value.toISOString(),
    end_date: endDate.value.toISOString(),
    electric_value: electricalEnergySum.value,
    co2_emissions: co2EmissionSum.value / 1000, // トレンドグラフで扱うCO2の単位はkg-CO2eで、カーボンフットプリントで扱うCO2の単位はt-CO2eなので、1000で割る
    scope_no: 2, // 電気なので2で固定
  });
};

onMounted(() => {
  updateDateRange();
});
</script>
