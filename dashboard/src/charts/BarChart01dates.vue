<template>
  <div class="grow">
    <canvas ref="canvas" :data="data" :width="width" :height="height"></canvas>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import {
  Chart,
  BarController,
  BarElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  CategoryScale,
} from 'chart.js';
import 'chartjs-adapter-moment';
import annotationPlugin from 'chartjs-plugin-annotation';

// Import utilities
import { tailwindConfig, formatValue } from '../utils/Utils';

Chart.register(
  BarController,
  BarElement,
  LinearScale,
  TimeScale,
  CategoryScale,
  annotationPlugin,
  Tooltip,
  Legend
);

export default {
  name: 'BarChart01',
  props: ['data', 'width', 'height', 'unit', 'fillXMin', 'fillXMax'],
  setup(props) {
    const canvas = ref(null);
    const legend = ref(null);
    let chart = null;

    watch(
      () => props.data,
      () => {
        if (chart) {
          chart.data = props.data;
          chart.update();
        }
      }
    );

    watch(
      () => props.fillXMin,
      () => {
        if (chart) {
          chart.options.plugins.annotation.annotations.box1.xMin =
            props.fillXMin;
          chart.update();
        }
      }
    );

    watch(
      () => props.fillXMax,
      () => {
        if (chart) {
          chart.options.plugins.annotation.annotations.box1.xMax =
            props.fillXMax;
          chart.update();
        }
      }
    );

    onMounted(() => {
      const ctx = canvas.value;
      chart = new Chart(ctx, {
        type: 'bar',
        data: props.data,
        options: {
          layout: {
            padding: {
              top: 30,
              bottom: 16,
              left: 24,
              right: 24,
            },
          },
          scales: {
            y: {
              border: {
                display: false,
              },
            },
            x: {
              ticks: {
                stepSize: 6,
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
              callbacks: {
                title: () => false, // Disable tooltip title
                // label: (context) => formatValue(context.parsed.y),
              },
            },
            datalabels: {
              display: false,
            },
            annotation: {
              annotations: {
                box1: {
                  type: 'box',
                  xMin: props.fillXMin ?? 0,
                  xMax: props.fillXMax ?? 0,
                  backgroundColor: 'rgba(255, 255, 132, 0.5)',
                  borderWidth: 0,
                },
              },
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
                li.style.marginRight = tailwindConfig().theme.margin[4];
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
                box.style.borderColor = item.fillStyle;
                box.style.pointerEvents = 'none';
                // Label
                const labelContainer = document.createElement('span');
                labelContainer.style.display = 'flex';
                labelContainer.style.alignItems = 'center';
                const value = document.createElement('span');
                value.style.color = tailwindConfig().theme.colors.slate[800];
                value.style.fontSize =
                  tailwindConfig().theme.fontSize['3xl'][0];
                value.style.lineHeight =
                  tailwindConfig().theme.fontSize['3xl'][1].lineHeight;
                value.style.fontWeight = tailwindConfig().theme.fontWeight.bold;
                value.style.marginRight = tailwindConfig().theme.margin[2];
                value.style.pointerEvents = 'none';
                const label = document.createElement('span');
                label.style.color = tailwindConfig().theme.colors.slate[500];
                label.style.fontSize = tailwindConfig().theme.fontSize.sm[0];
                label.style.lineHeight =
                  tailwindConfig().theme.fontSize.sm[1].lineHeight;
                const theValue = c.data.datasets[item.datasetIndex].data.reduce(
                  (a, b) => a + b,
                  0
                );
                const valueText = document.createTextNode(
                  formatValue(theValue)
                );
                const labelText = document.createTextNode(item.text);
                value.appendChild(valueText);
                label.appendChild(labelText);
                li.appendChild(button);
                button.appendChild(box);
                button.appendChild(labelContainer);
                labelContainer.appendChild(value);
                labelContainer.appendChild(label);
                ul.appendChild(li);
              });
            },
          },
          {
            id: 'afterDraw',
            afterDraw: (c) => {
              const ctx = c.ctx;
              ctx.save();
              ctx.fillStyle = '#000';
              ctx.font = 'bold';
              ctx.textAlign = 'right';
              ctx.fillText(props.unit, 40, 10);
              ctx.restore();
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
