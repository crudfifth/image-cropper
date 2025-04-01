// トレンドグラフ画面用の共有ストア

import { reactive } from 'vue';
import {
  getLastMonday,
  getFirstDayOfMonth,
  getLast30Minutes,
  getLast2Hour,
  getZeroOClock,
} from '@/utils/Utils';
import type { TimePeriodType, IntensityType, TrendGraphType } from '@/types';
import type { GraphKeyType } from '@/services/GraphService';
import type { ResponseType as GraphResponseType } from '@/services/GraphService';

export type GraphStateType = {
  timePeriod: TimePeriodType;
  startDates: Record<TimePeriodType, Date>;
  intensity: IntensityType;
  graphType: TrendGraphType;
  selectedGraphKeys: GraphKeyType[];
  unitSettingAvailable: boolean;
};

export const graphStateStore = reactive<GraphStateType>({
  timePeriod: 'day',
  startDates: {
    'four-hour': getLast30Minutes(getLast2Hour(new Date())),
    day: getZeroOClock(new Date()),
    week: getLastMonday(new Date()),
    month: getFirstDayOfMonth(new Date()),
    year: new Date(),
  },
  intensity: 'default',
  graphType: 'electricity',
  selectedGraphKeys: [],
  unitSettingAvailable: false,
});

export const graphDataStore = reactive({
  graphData: undefined as GraphResponseType | undefined,
  prevGraphData: undefined as GraphResponseType | undefined,
});

// カーボンフットプリントの設定用
type carbonFootprintRangeType = {
  startDate: Date;
  endDate: Date;
};

export const carbonFootprintStore = reactive<
  Record<TimePeriodType, carbonFootprintRangeType>
>({
  'four-hour': {
    startDate: getLast30Minutes(getLast2Hour(new Date())),
    endDate: getLast30Minutes(getLast2Hour(new Date())),
  },
  day: {
    startDate: getZeroOClock(new Date()),
    endDate: getZeroOClock(new Date()),
  },
  week: {
    startDate: getLastMonday(new Date()),
    endDate: getLastMonday(new Date()),
  },
  month: {
    startDate: getFirstDayOfMonth(new Date()),
    endDate: getFirstDayOfMonth(new Date()),
  },
  year: {
    startDate: new Date(),
    endDate: new Date(),
  },
});

export const resetCarbonFootprintStore = () => {
  carbonFootprintStore['four-hour'].startDate =
    graphStateStore.startDates['four-hour'];
  carbonFootprintStore['four-hour'].endDate =
    graphStateStore.startDates['four-hour'];
  carbonFootprintStore.day.startDate = graphStateStore.startDates.day;
  carbonFootprintStore.day.endDate = graphStateStore.startDates.day;
  carbonFootprintStore.week.startDate = graphStateStore.startDates.week;
  carbonFootprintStore.week.endDate = graphStateStore.startDates.week;
  carbonFootprintStore.month.startDate = graphStateStore.startDates.month;
  carbonFootprintStore.month.endDate = graphStateStore.startDates.month;
  carbonFootprintStore.year.startDate = graphStateStore.startDates.year;
  carbonFootprintStore.year.endDate = graphStateStore.startDates.year;
};
