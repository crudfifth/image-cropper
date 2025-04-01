<template>
  <div class="grow flex flex-col justify-center">
    <div>
      <canvas ref="canvas" :data="data" :width="width" :height="height">
      </canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, Ref } from 'vue';
import {
  Chart,
  DoughnutController,
  ArcElement,
  TimeScale,
  Tooltip,
} from 'chart.js';
import 'chartjs-adapter-moment';
import ChartDataLabels from 'chartjs-plugin-datalabels';

type ChartData = {
  labels: string[];
  datasets: {
    data: number[];
    backgroundColor: string[];
  }[];
};

Chart.register(
  DoughnutController,
  ArcElement,
  TimeScale,
  Tooltip,
  ChartDataLabels
);

const props = withDefaults(
  defineProps<{
    data: ChartData;
    width: number;
    height: number;
  }>(),
  {
    width: 270,
    height: 210,
  }
);

watch(
  () => props.data,
  () => {
    update();
  }
);

const canvas: Ref<HTMLCanvasElement | null> = ref(null);
let chart: Chart<'doughnut', number[], string> | null = null;

const update = () => {
  if (chart && props.data) {
    chart.data = props.data;
    chart.update();
  }
};

onMounted(() => {
  const ctx = canvas.value;
  if (!ctx || !props.data) {
    return;
  }
  chart = new Chart(ctx, {
    type: 'doughnut',
    data: props.data,
    options: {
      cutout: '40%',
      layout: {
        // padding: 24,
      },
      plugins: {
        legend: {
          display: false,
        },
        datalabels: {
          display: false,
        },
        tooltip: {
          enabled: false,
        },
      },
      interaction: {
        intersect: false,
        mode: 'nearest',
      },
      animation: {
        duration: 500,
      },
      maintainAspectRatio: false,
      resizeDelay: 200,
    },
  });
});

onUnmounted(() => chart?.destroy());
</script>
