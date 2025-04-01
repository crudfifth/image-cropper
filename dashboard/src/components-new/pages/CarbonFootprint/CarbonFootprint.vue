<template>
  <PageLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8 w-full">
      <div class="flex gap-6">
        <div class="max-w-100 min-w-100">
          <SidebarLayout
            :scope-data="scopeData"
            :loaded-pie-chart-data="loadedData"
            :pie-chart-data="scopePieChartData"
          />
        </div>
        <div class="flex flex-col w-full overflow-auto">
          <DashboardLayout
            :loaded-graph-data="loadedData"
            :pie-chart-data="co2EmissionPieChartData"
            :bar-chart-data="groupCo2EmissionChartData"
          />
          <DetailsLayout
            v-if="carbonFootPrint"
            :carbon-footprint="carbonFootPrint"
            @delete-carbon-footprint="onDeleteFootprint"
            @add-carbon-footprint="onAddFootprint"
            @update-carbon-footprint="fetchData"
          />
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import PageLayout from '@components/common/containers/PageLayout.vue';
import SidebarLayout from './containers/SidebarLayout.vue';
import DashboardLayout from './containers/DashboardLayout.vue';
import DetailsLayout from './containers/DetailsLayout.vue';
import type { PieChartDataType } from './containers/SidebarLayout.vue';
import CarbonFootprintService from '@/services/CarbonFootprintService';
import { CarbonFootprint } from '@/repositories/CarbonFootprintRepository';
import { filter } from 'lodash-es';

const loadedData = ref(false);
const scopePieChartData = ref<PieChartDataType>({
  labels: [],
  datasets: [{ data: [], backgroundColor: [] }],
});
const co2EmissionPieChartData = ref<PieChartDataType>({
  labels: [],
  datasets: [{ data: [], backgroundColor: [] }],
});
const groupCo2EmissionChartData = ref<PieChartDataType>({
  labels: [],
  datasets: [{ data: [], backgroundColor: [] }],
});

const scopeData = computed(() => {
  return [
    {
      name: 'Scope1（燃料）',
      value: scopePieChartData.value.datasets[0].data[0],
    },
    {
      name: 'Scope2（電気）',
      value: scopePieChartData.value.datasets[0].data[1],
    },
    {
      name: 'Scope3（原材料・輸送等）',
      value: scopePieChartData.value.datasets[0].data[2],
    },
  ];
});
const carbonFootPrint = ref<CarbonFootprint[] | undefined>(undefined);

const fetchData = async () => {
  const carbonFootprintScope =
    await CarbonFootprintService.fetchCarbonFootPrintScope();
  const labels = ['Scope1', 'Scope2', 'Scope3'];
  const dataList = [
    carbonFootprintScope.scope1,
    carbonFootprintScope.scope2,
    carbonFootprintScope.scope3,
  ];
  scopePieChartData.value = {
    labels: labels,
    datasets: [
      { data: dataList, backgroundColor: ['#BAE0FD', '#FDBABA', '#FFE283'] },
    ],
  };

  carbonFootPrint.value = await CarbonFootprintService.fetchCarbonFootprint();

  co2EmissionPieChartData.value =
    await CarbonFootprintService.generateGroupPieChartData(
      carbonFootPrint.value
    );

  groupCo2EmissionChartData.value =
    await CarbonFootprintService.generateGroupChartData(carbonFootPrint.value);
};

onMounted(async () => {
  await fetchData();
  loadedData.value = true;
  return;
});

const onDeleteFootprint = (id: string) => {
  carbonFootPrint.value = filter(carbonFootPrint.value, (footprint) => {
    return footprint.id !== id;
  });
};

const onAddFootprint = (footprint: CarbonFootprint) => {
  carbonFootPrint.value?.unshift(footprint);
  carbonFootPrint.value?.sort((a, b) => {
    if (a.process_name < b.process_name) return -1;
    if (a.process_name > b.process_name) return 1;
    return 0;
  });
};
</script>
