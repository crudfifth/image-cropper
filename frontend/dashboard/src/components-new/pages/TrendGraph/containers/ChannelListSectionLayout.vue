<!-- チャンネルリスト (メインエリア下側) -->
<template>
  <div class="grid grid-cols-12 gap-6 p-6">
    <div class="col-span-9">
      <div>
        <ChannelTable :graph-table-data="graphDataArray" />
      </div>
    </div>
    <div class="col-span-3">
      <!-- 円グラフ領域 -->
      <div class="text-right text-slate-700 rounded-md mb-8">
        <!-- 円グラフ本体 -->
        <DoughnutChart :data="pieChartData" :height="200" />
      </div>
      <ul class="text-right pr-2 max-h-32 overflow-auto flex flex-col text-lg">
        <!-- 凡例 -->
        <li
          v-for="(label, index) in pieChartData.labels"
          :key="label"
          class="flex justify-between items-center"
        >
          <span
            class="mx-2"
            :style="{ color: pieChartData.datasets[0].backgroundColor[index] }"
          >
            ■
          </span>
          <div class="flex-grow flex justify-between">
            <span class="text-sm">{{ label }}</span>
            <span class="text-sm">{{
              `${roundTwoDecimal(pieChartData.datasets[0].data[index])}%`
            }}</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { match } from 'ts-pattern';
import { range } from 'lodash-es';
import ChannelTable from './ChannelTable.vue';
import DoughnutChart from '../../../common/presenters/charts/DoughnutChart.vue';

import type {
  ResponseType as GraphResponseType,
  GraphKeyType,
} from '@/services/GraphService';
import { roundTwoDecimal } from '@/utils/Round';
import { graphDataStore, graphStateStore } from '@/stores/TrendGraphStore';

export type GraphTableValueType = {
  id: GraphKeyType;
  name: string;
  value: number;
  isEnabled: boolean;
};

const pieChartData = computed(() => {
  const valueSum = graphDataArray.value.reduce(
    (acc, cur) => acc + cur.value,
    0
  );

  const percentageGraphDataArray = graphDataArray.value.map((x) => ({
    ...x,
    percentage: roundTwoDecimal(valueSum ? (x.value / valueSum) * 100 : 0),
  }));

  // Array.prototype.sortが安定ソートであることを期待した実装。ES2019以降のArray.prototype.sortは安定ソート。
  const sortedGraphData = [...percentageGraphDataArray].sort(
    (a, b) => roundTwoDecimal(b.value) - roundTwoDecimal(a.value)
  );

  const result = [
    sortedGraphData[0],
    sortedGraphData[1],
    sortedGraphData[2],
    {
      id: 'other',
      name: sortedGraphData[0].value !== 0 ? 'その他合計' : '-',
      value: sortedGraphData.slice(3).reduce((acc, cur) => acc + cur.value, 0),
      percentage: 0,
    },
  ];

  result[3].percentage =
    sortedGraphData[0].value !== 0
      ? roundTwoDecimal(
          100 - result.slice(0, 3).reduce((acc, cur) => acc + cur.percentage, 0)
        )
      : 0; // パーセントの合計が必ず100になるように調整

  return {
    labels: result.map((x) => x.name),
    datasets: [
      {
        data: result.map((x) => x.percentage),
        backgroundColor: ['#FF5722', '#FF9900', '#FFC201', '#CEDD36'],
      },
    ],
  };
});

const graphDataArray = computed<GraphTableValueType[]>(() => {
  const graphArray = graphToArray(graphDataStore.graphData);
  return graphArray.map((g) => {
    const latestDataPoint = g.dataPoints.reduce((latest, current) => {
      const latestDate = new Date(
        latest.year,
        latest.month - 1,
        latest.date,
        latest.hour ?? 0,
        latest.minute ?? 0
      );
      const currentDate = new Date(
        current.year,
        current.month - 1,
        current.date,
        current.hour ?? 0,
        current.minute ?? 0
      );
      return currentDate > latestDate ? current : latest;
    }, g.dataPoints[0]);

    const value = latestDataPoint
      ? match(graphStateStore.graphType)
          .with('electricity', () => latestDataPoint.electrical_value)
          .with('utilityCost', () => latestDataPoint.electrical_price)
          .with('co2Emission', () => latestDataPoint.co2_value)
          .with('carbonCredit', () => latestDataPoint.co2_price_reduction)
          .with(
            'electricityReduction',
            () => latestDataPoint.electrical_value_reduction
          )
          .with(
            'utilityCostReduction',
            () => latestDataPoint.electrical_price_reduction
          )
          .with(
            'co2EmissionReduction',
            () => latestDataPoint.co2_value_reduction
          )
          .with('carbonFootprint', () => latestDataPoint.electrical_value)
          .exhaustive()
      : 0;

    return {
      id: g.id,
      name: g.name,
      isEnabled: g.isEnabled,
      value,
    };
  });
});

const graphToArray = (graph: GraphResponseType | undefined) => {
  const maxKey = 16;
  if (!graph) {
    const ret = range(1, maxKey + 1).map((key) => ({
      id: key.toString() as GraphKeyType,
      name: '-',
      dataPoints: [],
      isEnabled: false,
    }));
    return ret;
  }
  const ret = range(1, maxKey + 1).map((key) => {
    const keyLiteral = key.toString() as GraphKeyType;
    const g = graph?.[keyLiteral];
    if (!g) {
      return {
        id: keyLiteral,
        name: '-',
        dataPoints: [],
        isEnabled: false,
      };
    }
    return {
      id: keyLiteral,
      name: g.name,
      dataPoints: g.dataPoints,
      isEnabled: g.isEnabled,
    };
  });
  return ret;
};
</script>
