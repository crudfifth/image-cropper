<template>
  <div className="px-5 py-3">
    <div className="flex flex-wrap justify-between items-end">
      <div className="flex items-center">
        <div className="text-3xl font-bold text-slate-800 mr-2">244.7%</div>
        <div className="text-sm">
          <span className="font-medium text-slate-800">17.4%</span> AVG
        </div>
      </div>
      <div className="grow ml-2 mb-1">
        <ul ref="legend" className="flex flex-wrap justify-end" />
      </div>
    </div>
  </div>
  <!-- Chart built with Chart.js 3 -->
  <div className="grow">
    <canvas ref="canvas" :data="data" :width="width" :height="height"></canvas>
  </div>
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
import { tailwindConfig } from '../utils/Utils';

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
  name: 'LineChart05',
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
              ticks: {
                maxTicksLimit: 7,
                callback: (value) => `${value}%`,
              },
            },
            x: {
              type: 'time',
              time: {
                parser: 'MM-DD-YYYY',
                unit: 'month',
                displayFormats: {
                  month: 'MMM YY',
                },
              },
              border: {
                display: false,
              },
              grid: {
                display: false,
              },
              ticks: {
                autoSkipPadding: 48,
                maxRotation: 0,
              },
            },
          },
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                title: () => false, // Disable tooltip title
                label: (context) => `${context.parsed.y}%`,
              },
            },
          },
          interaction: {
            intersect: false,
            mode: 'nearest',
          },
          maintainAspectRatio: false,
        },
        plugins: [
          {
            id: 'htmlLegend',
            afterUpdate(c, args, options) {
              const ul = legend.value;
              if (!ul) return;
              // Remove old legend items
              while (ul.firstChild) {
                ul.firstChild.remove();
              }
              // Reuse the built-in legendItems generator
              const items = c.options.plugins.legend.labels.generateLabels(c);
              items.forEach((item) => {
                const li = document.createElement('li');
                li.style.marginLeft = tailwindConfig().theme.margin[3];
                // Button element
                const button = document.createElement('button');
                button.style.display = 'inline-flex';
                button.style.alignItems = 'center';
                button.style.opacity = item.hidden ? '.3' : '';
                button.onclick = () => {
                  c.setDatasetVisibility(
                    item.datasetIndex,
                    !c.isDatasetVisible(item.datasetIndex)
                  );
                  c.update();
                };
                // Color box
                const box = document.createElement('span');
                box.style.display = 'block';
                box.style.width = tailwindConfig().theme.width[3];
                box.style.height = tailwindConfig().theme.height[3];
                box.style.borderRadius =
                  tailwindConfig().theme.borderRadius.full;
                box.style.marginRight = tailwindConfig().theme.margin[2];
                box.style.borderWidth = '3px';
                box.style.borderColor =
                  c.data.datasets[item.datasetIndex].borderColor;
                box.style.pointerEvents = 'none';
                // Label
                const label = document.createElement('span');
                label.style.color = tailwindConfig().theme.colors.slate[500];
                label.style.fontSize = tailwindConfig().theme.fontSize.sm[0];
                label.style.lineHeight =
                  tailwindConfig().theme.fontSize.sm[1].lineHeight;
                const labelText = document.createTextNode(item.text);
                label.appendChild(labelText);
                li.appendChild(button);
                button.appendChild(box);
                button.appendChild(label);
                ul.appendChild(li);
              });
            },
          },
        ],
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
