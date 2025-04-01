<template>
  <PageLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-10xl mx-auto">
      <div class="flex gap-6">
        <!-- 左パネル領域 -->
        <LeftDockPanelLayout class="max-w-100 min-w-100" />
        <!-- メイン領域 -->
        <div class="flex flex-col w-full overflow-x-auto">
          <div class="flex flex-col bg-white shadow-lg rounded-md">
            <div class="p-6">
              <MainHeaderLayout />
              <MainChartSectionLayout />
              <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12">
                  <ChannelListSectionLayout />
                  <div class="flex items-center">
                    <AsyncFunctionButton
                      id="download-csv"
                      class="flex items-center gap-1 text-sm bg-white hover:bg-blue-500 hover:text-white mr-2 py-2 px-4 border-2 hover:border-transparent rounded"
                      :on-click-async="downloadCsv"
                    >
                      <CsvIcon color="text-main-blue" class="w-6 h-6 inline" />
                      {{ csvDownloadButtonText }}
                    </AsyncFunctionButton>
                    <div class="text-sm ml-2">
                      上記、トレンドグラフの表示期間におけるデータをダウンロードできます。
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <PredictionNote />
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { match } from 'ts-pattern';
import PageLayout from '@components/common/containers/PageLayout.vue';
import LeftDockPanelLayout from './containers/LeftDockPanelLayout.vue';
import PredictionNote from './containers/PredictionNote.vue';
import MainHeaderLayout from './containers/MainHeaderLayout.vue';
import MainChartSectionLayout from './containers/MainChartSectionLayout.vue';
import ChannelListSectionLayout from './containers/ChannelListSectionLayout.vue';

import AsyncFunctionButton from '../../common/presenters/buttons/AsyncFunctionButton.vue';

import GraphService from '@/services/GraphService';
import CsvService from '@/services/CsvService';
import EconomicActivityService from '@/services/EconomicActivityService';

import type { TimePeriodType, IntensityType, TrendGraphType } from '@/types';
import type { GraphKeyType } from '@/services/GraphService';
import { graphDataStore, graphStateStore } from '@/stores/TrendGraphStore';
import { getWeekIndexOfMonth } from '@/utils/Utils';
import CsvIcon from '@/components/icons/CsvIcon.vue';
import { onumber } from 'zod';

export type GraphStateType = {
  timePeriod: TimePeriodType;
  date: Date;
  startDates: Record<TimePeriodType, Date>;
  intensity: IntensityType;
  graphType: TrendGraphType;
  selectedGraphs: GraphKeyType[];
};

const fetchGraphDataPoints = async () => {
  const state = graphStateStore;
  const date = state.startDates[state.timePeriod];
  graphDataStore.graphData = await GraphService.fetchGraphDataPoints({
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    date: date.getDate(),
    hour: date.getHours(),
    minute: date.getMinutes(),
    mode: state.intensity,
    start: undefined,
    end: undefined,
    week: state.timePeriod === 'week' ? getWeekIndexOfMonth(date) : undefined,
    activityTypeId: undefined,
    fuelUnit: undefined,
    timePeriodType: state.timePeriod,
  });
};

const csvDownloadButtonText = ref('CSVダウンロード');

const fetchPrevGraphDataPoints = async () => {
  const state = graphStateStore;
  const date = state.startDates[state.timePeriod];
  if (state.timePeriod === 'four-hour') {
    return;
  }
  const prevDate = new Date(date);
  match(state.timePeriod)
    .with('day', () => prevDate.setDate(prevDate.getDate() - 1))
    .with('week', () => prevDate.setDate(prevDate.getDate() - 7))
    .with('month', () => prevDate.setMonth(prevDate.getMonth() - 1))
    .otherwise(() => prevDate.setDate(prevDate.getDate() - 1));

  graphDataStore.prevGraphData = await GraphService.fetchGraphDataPoints({
    year: prevDate.getFullYear(),
    month: prevDate.getMonth() + 1,
    date: prevDate.getDate(),
    hour: prevDate.getHours(),
    minute: prevDate.getMinutes(),
    mode: state.intensity,
    start: undefined,
    end: undefined,
    week:
      state.timePeriod === 'week' ? getWeekIndexOfMonth(prevDate) : undefined,
    activityTypeId: undefined,
    fuelUnit: undefined,
    timePeriodType: state.timePeriod,
  });
};

const downloadCsv = async () => {
  csvDownloadButtonText.value = 'ダウンロード中...';
  const graphStartDate: Date =
    graphStateStore.startDates[graphStateStore.timePeriod];

  // 特定のDateに対して、そのDateを含む4時間分/1日/1週間/1月の範囲を返す。
  // ユーティリティ関数化しても良いかも
  const [startDate, endDate] = match(graphStateStore.timePeriod)
    .with('four-hour', () => {
      const fourHoursLater = new Date(graphStartDate);
      fourHoursLater.setHours(fourHoursLater.getHours() + 4);
      return [graphStartDate, fourHoursLater];
    })
    .with('day', () => {
      const startOfDay = new Date(graphStartDate);
      startOfDay.setHours(0, 0, 0, 0);
      const endOfDay = new Date(graphStartDate);
      endOfDay.setHours(23, 59, 59, 0);
      return [startOfDay, endOfDay];
    })
    .with('week', () => {
      const startOfWeek = new Date(graphStartDate);
      startOfWeek.setHours(0, 0, 0, 0);
      while (startOfWeek.getDay() !== 1) {
        startOfWeek.setDate(startOfWeek.getDate() - 1);
      }
      const endOfWeek = new Date(startOfWeek);
      endOfWeek.setDate(endOfWeek.getDate() + 6);
      endOfWeek.setHours(23, 59, 59, 0);
      return [startOfWeek, endOfWeek];
    })
    .with('month', () => {
      const startOfMonth = new Date(graphStartDate);
      startOfMonth.setDate(1);
      startOfMonth.setHours(0, 0, 0, 0);
      const endOfMonth = new Date(startOfMonth);
      endOfMonth.setMonth(endOfMonth.getMonth() + 1);
      endOfMonth.setDate(endOfMonth.getDate() - 1);
      endOfMonth.setHours(23, 59, 59, 0);
      return [startOfMonth, endOfMonth];
    })
    .otherwise(() => [new Date(), new Date()]);

  await CsvService.fetchCsv({
    startDate: startDate,
    endDate: endDate,
  });
  csvDownloadButtonText.value = 'CSVダウンロード';
};

watch(
  () => graphStateStore.startDates,
  async () => {
    clearGraphs();
    await refetchGraphs();
  },
  { deep: true }
);

watch(
  () => graphStateStore.intensity,
  async () => {
    clearGraphs();
    await refetchGraphs();
  }
);

watch(
  () => graphStateStore.timePeriod,
  async () => {
    clearGraphs();
    await refetchGraphs();
  }
);

const clearGraphs = () => {
  graphDataStore.graphData = undefined;
  graphDataStore.prevGraphData = undefined;
};

const refetchGraphs = async () => {
  await Promise.all([fetchGraphDataPoints(), fetchPrevGraphDataPoints()]);
};

const updateUnitSettingAvailable = async () => {
  const periodStartDate =
    graphStateStore.startDates[graphStateStore.timePeriod];
  const year = periodStartDate.getFullYear();
  const month = periodStartDate.getMonth() + 1;
  graphStateStore.unitSettingAvailable =
    await EconomicActivityService.isUnitSettingAvailable(year, month);
};

watch(
  () => graphStateStore.startDates[graphStateStore.timePeriod],
  async () => {
    await updateUnitSettingAvailable();
  }
);

// TODO: 30秒ごとにfetchし直す

onMounted(async () => {
  await Promise.all([
    fetchGraphDataPoints(),
    fetchPrevGraphDataPoints(),
    updateUnitSettingAvailable(),
  ]);
});

onUnmounted(() => {
  clearGraphs();
});
</script>
