<template>
  <section class="pb-5">
    <h2 class="text-2xl font-bold mb-2">
      <component :is="iconComponent" class="w-6 h-6 mr-3 inline" />
      {{ titleText }}
    </h2>
    <h3 class="text-lg mb-2">
      <span class="font-bold">月初から前日までの実績値</span>
    </h3>
    <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md">
      <div class="pr-4">
        <span class="text-2xl font-bold">{{
          monthlyActualValue.toLocaleString()
        }}</span>
        <span class="text-ms">{{ energyUnitLabelText }}</span>
      </div>
    </div>
    <div class="flex justify-between items-center">
      <div class="flex items-center justify-end w-full">
        <span class="text-right text-ms mr-4">当月進捗率</span>
        <span class="text-2xl font-bold mr-1">{{
          monthlyRateValuePercentage
        }}</span>
        <span class="text-lg">%</span>
      </div>
    </div>
  </section>

  <section>
    <h3 class="text-lg mb-2">
      <span class="font-bold">月間目標値</span>
    </h3>
    <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md">
      <div class="pr-4">
        <span class="text-2xl font-bold">{{
          monthlyTargetValue.toLocaleString()
        }}</span>
        <span class="text-ms">{{ energyUnitLabelText }}</span>
      </div>
    </div>
  </section>
</template>
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { match } from 'ts-pattern';

import MoneyBagIcon from '@icons/MoneyBagIcon.vue';
import Co2Icon from '@icons/Co2Icon.vue';
import ElectricIcon from '@icons/ElectricIcon.vue';

import ActualValuesService from '@/services/ActualValuesService';

import { createGraphUnitLabelText } from '@/utils/EnergyTypeUtils';
import { roundTwoDecimal } from '@/utils/Round';
import { graphStateStore } from '@/stores/TrendGraphStore';

const iconComponent = computed(() =>
  match(graphStateStore.graphType)
    .with(
      'electricity',
      'electricityReduction',
      'carbonFootprint',
      () => ElectricIcon
    )
    .with(
      'utilityCost',
      'carbonCredit',
      'utilityCostReduction',
      () => MoneyBagIcon
    )
    .with('co2Emission', 'co2EmissionReduction', () => Co2Icon)
    .exhaustive()
);

const titleText = computed(() =>
  match(graphStateStore.graphType)
    .with('electricity', () => '電力量')
    .with('utilityCost', () => '光熱費')
    .with('co2Emission', () => 'CO₂排出量')
    .with('carbonCredit', () => 'カーボンクレジット量')
    .with('electricityReduction', () => '電力削減量')
    .with('utilityCostReduction', () => '光熱削減費')
    .with('co2EmissionReduction', () => 'CO₂削減量')
    .with('carbonFootprint', () => '電力量')
    .exhaustive()
);

// const energyUnitLabelText = computed(() =>
//   createGraphUnitLabelText({ graphType: graphStateStore.graphType })
// );
const isKgUnit = false;
const energyUnitLabelText = computed(() =>
  createGraphUnitLabelText({
     graphType: graphStateStore.graphType,
     isKgUnit: isKgUnit
  })
);

const monthlyActualValue = ref<number>(0);
const monthlyTargetValue = ref<number>(0);
const monthlyRateValuePercentage = ref<number>(0);

const updateValues = async () => {
  match(graphStateStore.graphType)
    .with('electricity', () => fetchElectrical())
    .with('utilityCost', () => fetchUtilityCosts())
    .with('co2Emission', () => fetchCo2())
    .with('carbonCredit', () => fetchCarbonCredit())
    .with('electricityReduction', () => fetchReductionElectrical())
    .with('utilityCostReduction', () => fetchReductionUtilityCosts())
    .with('co2EmissionReduction', () => fetchReductionCo2Emissions())
    .with('carbonFootprint', () => fetchElectrical())
    .exhaustive();
};

const fetchElectrical = async () => {
  const response = await ActualValuesService.fetchValuesElectrical();
  monthlyActualValue.value = roundTwoDecimal(response.actual_value);
  monthlyTargetValue.value = roundTwoDecimal(response.target_value);
  monthlyRateValuePercentage.value = roundTwoDecimal(response.rate_value * 100);
};

const fetchUtilityCosts = async () => {
  const response = await ActualValuesService.fetchValuesUtilityCosts();
  monthlyActualValue.value = Math.round(response.actual_value);
  monthlyTargetValue.value = Math.round(response.target_value);
  monthlyRateValuePercentage.value = roundTwoDecimal(response.rate_value * 100);
};

const fetchCo2 = async () => {
  const response = await ActualValuesService.fetchValuesCo2Emissions();
  monthlyActualValue.value = roundTwoDecimal(response.actual_value);
  monthlyTargetValue.value = roundTwoDecimal(response.target_value);
  monthlyRateValuePercentage.value = roundTwoDecimal(response.rate_value * 100);
};

const fetchCarbonCredit = async () => {
  const response = await ActualValuesService.fetchValuesCarbonCredit();
  monthlyActualValue.value = Math.round(response.actual_value);
  monthlyTargetValue.value = Math.round(response.target_value);
  monthlyRateValuePercentage.value = roundTwoDecimal(response.rate_value * 100);
};

const fetchReductionElectrical = async () => {
  const response = await ActualValuesService.fetchValuesReductionElectrical();
  monthlyActualValue.value = roundTwoDecimal(response.actual_value);
  monthlyTargetValue.value = roundTwoDecimal(response.target_value);
  monthlyRateValuePercentage.value = roundTwoDecimal(response.rate_value * 100);
};

const fetchReductionUtilityCosts = async () => {
  const response = await ActualValuesService.fetchValuesReductionUtilityCosts();
  monthlyActualValue.value = Math.round(response.actual_value);
  monthlyTargetValue.value = Math.round(response.target_value);
  monthlyRateValuePercentage.value = roundTwoDecimal(response.rate_value * 100);
};

const fetchReductionCo2Emissions = async () => {
  const response = await ActualValuesService.fetchValuesReductionCo2Emissions();
  monthlyActualValue.value = roundTwoDecimal(response.actual_value);
  monthlyTargetValue.value = roundTwoDecimal(response.target_value);
  monthlyRateValuePercentage.value = roundTwoDecimal(response.rate_value * 100);
};

watch(
  () => graphStateStore.graphType,
  () => {
    updateValues();
  }
);

onMounted(() => {
  updateValues();
});
</script>
