<template>
  <canvas ref="canvas" :data="data" :width="width" :height="height"></canvas>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import {
  Chart,
  LineController,
  LineElement,
  Filler,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
} from 'chart.js';
import 'chartjs-adapter-moment';

// Import utilities
import { formatThousands } from '../utils/Utils';

Chart.register(
  LineController,
  LineElement,
  Filler,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip
);

export default {
  name: 'LineChart03',
  props: ['data', 'width', 'height'],
  setup(props) {
    const canvas = ref(null);
    const legend = ref(null);
    let chart = null;

    onMounted(() => {
      const ctx = canvas.value;
      chart = new Chart(ctx, {
        type: 'line',
        data: props.data,
        options: {
          layout: {
            padding: 20,
          },
          scales: {
            y: {
              beginAtZero: true,
              border: {
                display: false,
              },
              // ticks: {
              //   callback: (value) => formatThousands(value),
              // },
            },
            x: {
              type: 'time',
              time: {
                parser: 'MM-DD-YYYY',
                unit: 'month',
                displayFormats: {
                  month: 'MMM',
                },
              },
              border: {
                display: false,
              },
              grid: {
                display: false,
              },
              // ticks: {
              //   autoSkipPadding: 48,
              //   maxRotation: 0,
              // },
            },
          },
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                title: () => false, // Disable tooltip title
                label: (context) => formatThousands(context.parsed.y),
              },
            },
          },
          interaction: {
            intersect: false,
            mode: 'nearest',
          },
          maintainAspectRatio: false,
          resizeDelay: 200,
        },
      });
    });

    onUnmounted(() => chart.destroy());

    return {
      canvas,
      legend,
    };
  },
};
</script>
