<template>
  <div class="flex flex-col bg-white shadow-lg rounded-md mb-4">
    <div class="grid grid-cols-12 gap-6 p-6">
      <div class="col-span-12">
        <div>
          <h2 class="text-2xl font-bold flex items-center">
            <TachometerIcon class="mr-3" />
            ダッシュボード
          </h2>

          <div class="flex justify-around items-start overflow-x-auto">
            <div class="flex items-center">
              <div>
                <DoughnutChart
                  v-if="loadedGraphData"
                  class="col-span-6 mt-7 mx-auto"
                  :data="pieChartData"
                  :width="270"
                  :height="210"
                />
              </div>
              <ul class="text-sm">
                <li v-for="(label, i) in pieChartData.labels" :key="label">
                  <div
                    class="h-[12px] w-[12px] inline-block"
                    :style="`background-color: ${pieChartData.datasets[0].backgroundColor[i]}`"
                  ></div>
                  <span class="font-bold ml-1">{{ label }}</span>
                  <span class="ml-2">{{ calcPercents(i) }}%</span>
                </li>
              </ul>
            </div>

            <div>
              <!-- TODO: ChartのW/Hが固定値になっているので修正する -->
              <BarChart
                v-if="loadedGraphData"
                class="col-span-6 mt-7 mx-auto"
                :data="barChartData"
                :width="680"
                :height="210"
                unit="t-CO₂e"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DoughnutChart from '@charts/DoughnutChart.vue';
import BarChart from '@charts/BarChart.vue';
import TachometerIcon from '@icons/TachometerIcon.vue';

// TODO: 型定義をChart側に移す
export type PieChartDataType = {
  labels: string[];
  datasets: { data: number[]; backgroundColor: string[] }[];
};

// TODO: 型定義をChart側に移す
export type BarChartDataType = {
  labels: string[];
  datasets: { data: number[]; backgroundColor: string[] }[];
};

const props = defineProps({
  loadedGraphData: { type: Boolean, required: true },
  pieChartData: { type: Object as () => PieChartDataType, required: true },
  barChartData: { type: Object as () => BarChartDataType, required: true },
});

const calcPercents = (index: number) => {
  const data = props.pieChartData.datasets[0].data;
  const total = data.reduce((acc, cur) => acc + cur, 0);
  return data[index] ? ((data[index] / total) * 100).toFixed(1) : 0;
};
</script>
