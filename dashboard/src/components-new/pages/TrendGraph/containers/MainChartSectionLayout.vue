<template>
  <BarChart
    :data="chartData"
    :unit="unitText"
    :fill-x-min="fillXMin"
    :fill-x-max="fillXMax"
    width="595"
    height="248"
  />
</template>
<script setup lang="ts">
import { computed } from 'vue';
import BarChart from '../../../common/presenters/charts/BarChart01dates.vue';
import type { TrendGraphType } from '@/types';
import type {
  ResponseType as GraphResponseType,
  DataPointType,
  GraphKeyType,
} from '@/services/GraphService';
import {
  carbonFootprintStore,
  graphStateStore,
  graphDataStore,
} from '@/stores/TrendGraphStore';
import { createTimeSeriesDataLabels } from '@/utils/TimeSeriesDataUtils';
import { createGraphUnitLabelText } from '@/utils/EnergyTypeUtils';
import { match } from 'ts-pattern';
import { ChartData } from 'chart.js';
import { ChartDataset } from 'chart.js';

const fillXMin = computed(() => {
  return dateToIndex(
    carbonFootprintStore[graphStateStore.timePeriod].startDate
  );
});

const fillXMax = computed(() => {
  return dateToIndex(carbonFootprintStore[graphStateStore.timePeriod].endDate);
});

// const unitText = computed(() =>
//   createGraphUnitLabelText({ graphType: graphStateStore.graphType })
// );

const unitText = computed(() =>
  createGraphUnitLabelText({
    graphType: graphStateStore.graphType,
    isKgUnit: true,
  })
);

const createChartDataset = (
  graphData: GraphResponseType,
  settings: Partial<ChartDataset<'bar' | 'line'>>
): ChartDataset<'bar' | 'line'> => ({
  data:
    createTimeSeriesChartValues({
      graphData,
      selectedGraphKeys: graphStateStore.selectedGraphKeys,
      graphType: graphStateStore.graphType,
    }) ?? [],
  ...settings,
});

const chartData = computed<ChartData<'bar' | 'line'>>(() => {
  const labels = createTimeSeriesDataLabels({
    timePeriod: graphStateStore.timePeriod,
    startDate: graphStateStore.startDates[graphStateStore.timePeriod],
  });

  if (graphStateStore.timePeriod === 'four-hour' && graphDataStore.graphData) {
    // MEMO: 4時間単位のグラフは前回のデータがないので、現在のデータのみ表示する
    return {
      labels,
      datasets: [
        createChartDataset(graphDataStore.graphData, {
          type: 'bar',
          backgroundColor: '#F0A1A1',
          order: 2,
        }),
      ],
    };
  } else if (graphDataStore.graphData && graphDataStore.prevGraphData) {
    return {
      labels,
      datasets: [
        createChartDataset(graphDataStore.graphData, {
          type: 'bar',
          backgroundColor: '#F0A1A1',
          hoverBackgroundColor: '#FF5722',
          order: 2,
        }),
        createChartDataset(graphDataStore.prevGraphData, {
          type: 'line',
          borderColor: '#00559A',
          borderWidth: 2,
          pointRadius: 1,
          order: 1,
        }),
      ],
    };
  }

  return {
    labels,
    datasets: [],
  };
});

const createFourHourValues = (input: {
  dataPoints: DataPointType[];
  valueSelector: (item: DataPointType) => number;
  startDate: Date;
}) => {
  const values: number[] = Array(240).fill(0); // 1分刻み4時間分
  input.dataPoints.forEach((item) => {
    const dataPointDate = new Date(
      item.year,
      item.month - 1,
      item.date,
      item.hour || 0,
      item.minute || 0
    );

    const elapsedMilliseconds =
      dataPointDate.getTime() - input.startDate.getTime();
    const elapsedMinutes = Math.floor(elapsedMilliseconds / (1000 * 60));
    values[elapsedMinutes] += input.valueSelector(item);
  });

  return values;
};

const createDayValues = (input: {
  dataPoints: DataPointType[];
  valueSelector: (item: DataPointType) => number;
}) => {
  const values: number[] = Array(48).fill(0);
  input.dataPoints.forEach((item) => {
    if (item.hour === undefined) {
      return;
    }
    const index = item.hour * 2 + Math.floor((item.minute ?? 0) / 30);
    values[index] += input.valueSelector(item);
  });
  return values;
};

const createWeekValues = (input: {
  dataPoints: DataPointType[];
  valueSelector: (item: DataPointType) => number;
}) => {
  const values: number[] = Array(7).fill(0);

  if (input.dataPoints.length === 0) {
    return values;
  }
  input.dataPoints.forEach((item) => {
    const itemDate = new Date(item.year, item.month - 1, item.date);
    const dayOfWeek = itemDate.getDay();
    const index = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
    values[index] += input.valueSelector(item);
  });

  return values;
};

const createMonthValues = (input: {
  dataPoints: DataPointType[];
  valueSelector: (item: DataPointType) => number;
}) => {
  const values: number[] = Array(31).fill(0);

  input.dataPoints.forEach((item) => {
    if (item.date === undefined) {
      return;
    }
    const index = item.date - 1;
    values[index] += input.valueSelector(item);
  });
  return values;
};

const createTimeSeriesChartValues = (input: {
  graphData: GraphResponseType | undefined;
  selectedGraphKeys: GraphKeyType[];
  graphType: TrendGraphType;
}) => {
  if (!input.graphData) {
    return;
  }

  const graphs = input.selectedGraphKeys.map((key) => input.graphData?.[key]);

  const dataPoints = graphs
    .flatMap((graph) => graph?.dataPoints)
    .filter((x): x is DataPointType => x !== undefined);

  const valueSelector = (item: DataPointType) => {
    return match(input.graphType)
      .with('electricity', () => item.electrical_value)
      .with('utilityCost', () => item.electrical_price)
      .with('co2Emission', () => item.co2_value)
      .with('carbonCredit', () => item.co2_price_reduction)
      .with('electricityReduction', () => item.electrical_value_reduction)
      .with('utilityCostReduction', () => item.electrical_price_reduction)
      .with('co2EmissionReduction', () => item.co2_value_reduction)
      .with('carbonFootprint', () => item.electrical_value)
      .exhaustive();
  };

  return match(graphStateStore.timePeriod)
    .with('four-hour', () => {
      return createFourHourValues({
        dataPoints,
        valueSelector,
        startDate: graphStateStore.startDates['four-hour'],
      });
    })
    .with('day', () => {
      return createDayValues({
        dataPoints,
        valueSelector,
      });
    })
    .with('week', () => {
      return createWeekValues({
        dataPoints,
        valueSelector,
      });
    })
    .with('month', () => {
      return createMonthValues({
        dataPoints,
        valueSelector,
      });
    })
    .otherwise(() => {
      return createDayValues({
        dataPoints,
        valueSelector,
      });
    });
};

const dateToIndex = (date: Date) => {
  return match(graphStateStore.timePeriod)
    .with('four-hour', () => {
      const startDate = graphStateStore.startDates['four-hour'];
      const diff = date.getTime() - startDate.getTime();
      // 差分を1分単位のインデックスに変換
      const ret = Math.floor(diff / (1000 * 60));
      return ret;
    })
    .with('day', () => {
      return date.getHours() * 2 + Math.floor(date.getMinutes() / 30);
    })
    .with('week', () => {
      return (date.getDay() + 6) % 7; // 月曜日で始まるインデックス
    })
    .with('month', () => {
      return date.getDate() - 1;
    })
    .otherwise(() => {
      return date.getHours() * 2 + Math.floor(date.getMinutes() / 30);
    });
};
</script>
