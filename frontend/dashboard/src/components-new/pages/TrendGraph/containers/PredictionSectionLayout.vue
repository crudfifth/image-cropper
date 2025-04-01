<template>
  <h2 class="text-2xl font-bold mb-2">
    <GraphIcon class="w-6 h-6 inline" />
    予測値
  </h2>
  <h3 class="text-lg mb-2">
    <span v-if="selectedDate" class="font-bold"
      >{{ selectedDate.getMonth() + 1 }}月予測値</span
    >
  </h3>
  <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md mb-3">
    <div class="pr-4">
      <span class="text-2xl font-bold">
        {{ monthlyPredictionValue.toLocaleString() }}
      </span>
      <span class="text-ms">{{ energyUnitLabelText }}</span>
    </div>
  </div>

  <h3 class="text-lg mb-2">
    <span class="font-bold">年間予測値 <small class="text-xs">※1月1日起点で積算し予測しています。</small></span>
  </h3>
  <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md mb-3">
    <div class="pr-4">
      <span class="text-2xl font-bold"
        >{{ yearlyPredictionValue.toLocaleString() }}
      </span>
      <span class="text-ms">{{ energyUnitLabelText }}</span>
    </div>
  </div>

  <h3 class="text-lg mb-2">
    <span class="font-bold">年間目標値</span>
  </h3>
  <div class="text-right text-slate-700 bg-sky-50 p-2 rounded-md mb-3">
    <div class="pr-4">
      <span class="text-2xl font-bold">{{
        yearlyTargetValue.toLocaleString()
      }}</span>
      <span class="text-ms">{{ energyUnitLabelText }}</span>
    </div>
  </div>

  <h3 class="text-lg mb-2">
    <span class="font-bold">目標値に対する予測値の割合</span>
  </h3>
  <ImprovementRateView :improvement-rate="yearlyImprovementRate" />
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { match } from 'ts-pattern';
import { createGraphUnitLabelText } from '@/utils/EnergyTypeUtils';
import { roundTwoDecimal } from '@/utils/Round';
import PredictedValuesService from '@/services/PredictedValuesService';
import { graphStateStore } from '@/stores/TrendGraphStore';
import ImprovementRateView from '../presenters/ImprovementRateView.vue';

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

const selectedDate = new Date(); // 予測値の月選択機能がまだないので、差し当たり。

const monthlyPredictionValue = ref(0);
const yearlyPredictionValue = ref(0);
const yearlyTargetValue = ref(0);
const yearlyImprovementRate = ref(0);

const updateValues = async () => {
  await match(graphStateStore.graphType)
    .with('electricity', async () => {
      await fetchElectrical();
    })
    .with('utilityCost', async () => {
      await fetchUtilityCosts();
    })
    .with('co2Emission', async () => {
      await fetchCo2Emissions();
    })
    .with('carbonCredit', async () => {
      await fetchCarbonCredit();
    })
    .with('electricityReduction', async () => {
      await fetchReductionElectrical();
    })
    .with('utilityCostReduction', async () => {
      await fetchReductionUtilityCosts();
    })
    .with('co2EmissionReduction', async () => {
      await fetchReductionCo2Emissions();
    })
    .with('carbonFootprint', async () => {
      // do nothing
    })
    .exhaustive();
};

// TODO: 予測値取得APIのレスポンスの型が同じになったので、取得部分を抽象化する
const fetchElectrical = async () => {
  const response =
    await PredictedValuesService.fetchPredictedValuesElectrical();
  monthlyPredictionValue.value = roundTwoDecimal(
    response.monthly_prediction_value
  );
  yearlyPredictionValue.value = roundTwoDecimal(
    response.yearly_prediction_value
  );
  yearlyTargetValue.value = roundTwoDecimal(response.yearly_target_value);
  yearlyImprovementRate.value = Math.round(
    response.yearly_improvement_rate * 100
  );
};

const fetchUtilityCosts = async () => {
  const response =
    await PredictedValuesService.fetchPredictedValuesUtilityCosts();
  monthlyPredictionValue.value = Math.round(response.monthly_prediction_value);
  yearlyPredictionValue.value = Math.round(response.yearly_prediction_value);
  yearlyTargetValue.value = Math.round(response.yearly_target_value);
  yearlyImprovementRate.value = Math.round(
    response.yearly_improvement_rate * 100
  );
};

const fetchCo2Emissions = async () => {
  const response =
    await PredictedValuesService.fetchPredictedValuesCo2Emissions();
  monthlyPredictionValue.value = roundTwoDecimal(
    response.monthly_prediction_value
  );
  yearlyPredictionValue.value = roundTwoDecimal(
    response.yearly_prediction_value
  );
  yearlyTargetValue.value = roundTwoDecimal(response.yearly_target_value);
  yearlyImprovementRate.value = Math.round(
    response.yearly_improvement_rate * 100
  );
};

const fetchCarbonCredit = async () => {
  const response =
    await PredictedValuesService.fetchPredictedValuesCarbonCredit();
  monthlyPredictionValue.value = Math.round(response.monthly_prediction_value);
  yearlyPredictionValue.value = Math.round(response.yearly_prediction_value);
  yearlyTargetValue.value = Math.round(response.yearly_target_value);
  yearlyImprovementRate.value = Math.round(
    response.yearly_improvement_rate * 100
  );
};

const fetchReductionElectrical = async () => {
  const response =
    await PredictedValuesService.fetchPredictedValuesReductionElectrical();
  monthlyPredictionValue.value = roundTwoDecimal(
    response.monthly_prediction_value
  );
  yearlyPredictionValue.value = roundTwoDecimal(
    response.yearly_prediction_value
  );
  yearlyTargetValue.value = roundTwoDecimal(response.yearly_target_value);
  yearlyImprovementRate.value = Math.round(
    response.yearly_improvement_rate * 100
  );
};

const fetchReductionUtilityCosts = async () => {
  const response =
    await PredictedValuesService.fetchPredictedValuesReductionUtilityCosts();
  monthlyPredictionValue.value = Math.round(response.monthly_prediction_value);
  yearlyPredictionValue.value = Math.round(response.yearly_prediction_value);
  yearlyTargetValue.value = Math.round(response.yearly_target_value);
  yearlyImprovementRate.value = Math.round(
    response.yearly_improvement_rate * 100
  );
};

const fetchReductionCo2Emissions = async () => {
  const response =
    await PredictedValuesService.fetchPredictedValuesReductionCo2Emissions();
  monthlyPredictionValue.value = roundTwoDecimal(
    response.monthly_prediction_value
  );
  yearlyPredictionValue.value = roundTwoDecimal(
    response.yearly_prediction_value
  );
  yearlyTargetValue.value = roundTwoDecimal(response.yearly_target_value);
  yearlyImprovementRate.value = Math.round(
    response.yearly_improvement_rate * 100
  );
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
