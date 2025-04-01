```
<template>
  <div class="col-span-3">
    <div
      class="mb-6 flex flex-col col-span-4 text-white bg-main-blue shadow-lg rounded-md"
    >
      <div class="p-6">
        <section class="pb-5 border-b">
          <h2 class="text-2xl font-bold mb-2">
            <CarbonFootprintIcon
              color="text-white"
              class="w-6 h-6 inline mb-1"
            />
            カーボンフットプリント
          </h2>
          <h3 class="text-lg mb-2">
            <span class="font-bold">GHG排出量 t-CO₂e</span>
          </h3>
          <div
            class="flex justify-end text-slate-700 bg-sky-50 rounded-md border-3 border-blue-300"
          >
            <div class="p-2">
              <span class="text-3xl font-bold">
                {{ (roundTwoDecimal(totalEmissions) || 0).toLocaleString() }}
              </span>
              <span class="text-ms px-2">t-CO₂e</span>
            </div>
          </div>
        </section>
        <div>
          <section class="pt-5">
            <div v-for="scope in scopeData" :key="scope.name" class="mb-4">
              <h3 class="font-bold mb-2">{{ scope.name }}</h3>
              <div class="text-right bg-sky-50 p-2 rounded-md">
                <span class="text-2xl font-bold text-slate-700">
                  {{ (roundTwoDecimal(scope.value) || 0).toLocaleString() }}
                </span>
                <span class="text-ms text-slate-700 px-2">t-CO₂e</span>
              </div>
            </div>
          </section>
          <div class="flex justify-between mt-2 w-24 w-full">
            <DoughnutChart
              v-if="loadedPieChartData"
              class="col-span-6 mt-7 mx-auto w-24"
              :data="scopeChartData"
              :width="270"
              :height="210"
            />
            <ul class="flex flex-col justify-center mt-7 text-sm pl-2">
              <li v-for="(label, i) in pieChartData.labels" :key="`label-${i}`">
                <div class="flex items-center justify-between w-full">
                  <div class="flex items-center">
                    <div
                      class="h-[12px] w-[12px] mr-2"
                      :style="`background-color: ${pieChartData.datasets[0].backgroundColor[i]}`"
                    ></div>
                    {{ label }}:
                  </div>
                  <div class="flex items-center">
                    <span class="font-bold">{{
                      roundTwoDecimal(pieChartData.datasets[0].data[i])
                    }}</span>
                    <span class="text-xs text-white text-slate-700 px-2"
                      >t-CO₂e</span
                    >
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { roundTwoDecimal } from '@/utils/Round';
import CarbonFootprintIcon from '@icons/CarbonFootprintIcon.vue';
import DoughnutChart from '@charts/DoughnutChart.vue';
export type PieChartDataType = {
  labels: string[];
  datasets: { data: number[]; backgroundColor: string[] }[];
};
const props = defineProps({
  loadedPieChartData: {
    type: Boolean,
    required: true,
  },
  pieChartData: {
    type: Object as () => PieChartDataType,
    required: true,
  },
  scopeData: {
    type: Array as () => { name: string; value: number }[],
    required: true,
  },
});
const totalEmissions = computed(() => {
  return props.scopeData.reduce((acc, scope) => acc + scope.value, 0);
});
const screenWidth = ref(window.innerWidth);
const handleResize = () => {
  screenWidth.value = window.innerWidth;
};
onMounted(() => {
  window.addEventListener('resize', handleResize);
});
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
const scopeChartData = computed(() => {
  return props.pieChartData;
});
</script>
```
