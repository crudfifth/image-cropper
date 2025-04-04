<template>
  <div class="px-5 py-4">
    <ul ref="legend" class="flex flex-wrap"></ul>
  </div>
  <div class="grow">
    <canvas ref="canvas" :data="data" :width="width" :height="height"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import {
  Chart,
  BarController,
  BarElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
} from 'chart.js';
import 'chartjs-adapter-moment';

// Import utilities
import { tailwindConfig, formatValue } from '../utils/Utils';

// Import images
import revolutIcon from '../images/company-icon-01.svg';
import hsbcIcon from '../images/company-icon-02.svg';
import qontoIcon from '../images/company-icon-03.svg';
import n26Icon from '../images/company-icon-04.svg';

Chart.register(
  BarController,
  BarElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend
);
const images = [revolutIcon, hsbcIcon, qontoIcon, n26Icon];

export default {
  name: 'BarChart06',
  props: ['data', 'width', 'height'],
  setup(props) {
    const canvas = ref(null);
    const legend = ref(null);
    let chart = null;

    onMounted(() => {
      const ctx = canvas.value;
      chart = new Chart(ctx, {
        type: 'bar',
        data: props.data,
        options: {
          indexAxis: 'y',
          layout: {
            padding: {
              top: 0,
              bottom: 0,
              left: 8,
              right: 8,
            },
          },
          scales: {
            y: {
              border: {
                display: false,
              },
              grid: {
                display: false,
                drawTicks: false,
              },
              ticks: {
                display: false,
              },
              stacked: true,
            },
            x: {
              border: {
                display: false,
              },
              ticks: {
                maxTicksLimit: 3,
                align: 'end',
                // callback: (value) => formatValue(value),
              },
              stacked: true,
            },
          },
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                title: () => false, // Disable tooltip title
                label: (context) => formatValue(context.parsed.x),
              },
            },
            datalabels: {
              display: false,
            },
          },
          // interaction: {
          //   intersect: false,
          //   mode: 'nearest',
          // },
          animation: {
            duration: 500,
          },
          maintainAspectRatio: false,
          resizeDelay: 200,
        },
        // plugins: [{
        //   id: 'htmlLegend',
        //   afterUpdate(c, args, options) {
        //     const ul = legend.value
        //     if (!ul) return
        //     // Remove old legend items
        //     while (ul.firstChild) {
        //       ul.firstChild.remove()
        //     }
        //     // Reuse the built-in legendItems generator
        //     const items = c.options.plugins.legend.labels.generateLabels(c)
        //     items.forEach((item) => {
        //       const li = document.createElement('li')
        //       li.style.marginRight = tailwindConfig().theme.margin[4]
        //       // Button element
        //       const button = document.createElement('button')
        //       button.style.display = 'inline-flex'
        //       button.style.alignItems = 'center'
        //       button.style.opacity = item.hidden ? '.3' : ''
        //       button.onclick = () => {
        //         c.setDatasetVisibility(item.datasetIndex, !c.isDatasetVisible(item.datasetIndex))
        //         c.update()
        //       }
        //       // Color box
        //       const box = document.createElement('span')
        //       box.style.display = 'block'
        //       box.style.width = tailwindConfig().theme.width[3]
        //       box.style.height = tailwindConfig().theme.height[3]
        //       box.style.borderRadius = tailwindConfig().theme.borderRadius.full
        //       box.style.marginRight = tailwindConfig().theme.margin[2]
        //       box.style.borderWidth = '3px'
        //       box.style.borderColor = item.fillStyle
        //       box.style.pointerEvents = 'none'
        //       // Label
        //       const label = document.createElement('span')
        //       label.style.color = tailwindConfig().theme.colors.slate[500]
        //       label.style.fontSize = tailwindConfig().theme.fontSize.sm[0]
        //       label.style.lineHeight = tailwindConfig().theme.fontSize.sm[1].lineHeight
        //       const labelText = document.createTextNode(item.text)
        //       label.appendChild(labelText)
        //       li.appendChild(button)
        //       button.appendChild(box)
        //       button.appendChild(label)
        //       ul.appendChild(li)
        //     })
        //   },
        //   afterDraw(c) {
        //     const xAxis = c.scales.x;
        //     const yAxis = c.scales.y;
        //     yAxis.ticks.forEach((value, index) => {
        //       const y = yAxis.getPixelForTick(index);
        //       const image = new Image();
        //       image.src = images[index];
        //       c.ctx.drawImage(image, xAxis.left - 52, y - 18);
        //     });
        //   },
        // }],
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
