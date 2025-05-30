<template>
  <canvas ref="canvas" :data="data" :width="width" :height="height"></canvas>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, Ref } from 'vue';
import {
  Chart,
  BarController,
  BarElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
} from 'chart.js';
import 'chartjs-adapter-moment';

export type PieChartDataType = {
  labels: string[];
  datasets: { data: number[]; backgroundColor: string[] }[];
};

Chart.register(
  BarController,
  BarElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend
);

const props = defineProps<{
  data: PieChartDataType;
  width: number;
  height: number;
  unit: string | undefined;
}>();

watch(
  () => props.data,
  () => {
    update();
  }
);

let chart: Chart<'bar', number[], string> | null = null;
const canvas: Ref<HTMLCanvasElement | null> = ref(null);

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
    type: 'bar',
    data: props.data,
    options: {
      layout: {
        padding: {
          top: 36,
          bottom: 16,
          left: 24,
          right: 20,
        },
      },
      scales: {
        y: {
          stacked: true,
          border: {
            display: false,
          },
          beginAtZero: true,
          ticks: {
            maxTicksLimit: 5,
          },
        },
        x: {
          stacked: true,
          border: {
            display: false,
          },
          grid: {
            display: false,
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          enabled: false,
        },
        datalabels: {
          display: false,
        },
      },
      interaction: {
        intersect: false,
        mode: 'nearest',
      },
      animation: {
        duration: 200,
      },
      maintainAspectRatio: false,
      resizeDelay: 200,
    },
    plugins: [
      {
        id: 'afterDraw',
        afterDraw: (c) => {
          const ctx = c.ctx;
          const yAxis = c.scales.y;
          ctx.save();
          ctx.fillStyle = '#000';
          ctx.font = 'bold';
          ctx.textAlign = 'right';
          ctx.fillText(props.unit ?? '', yAxis.left + 24, yAxis.top - 20);
          ctx.restore();
        },
      },
    ],
  });
});
onUnmounted(() => chart?.destroy());
</script>
