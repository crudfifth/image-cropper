<template>
  <div
    class="p-6 flex flex-col col-span-4 text-white bg-main-blue shadow-lg rounded-md"
  >
    <div v-if="annualPlanValues">
      <div class="flex justify-between items-end mb-4">
        <h2 class="text-lg font-bold">年間目標値</h2>
        <SubmitButton
          :on-click-async="saveAnnualPlanValues"
          :disabled="!isValidAnnualValues"
        />
      </div>
      <AnnualValueInput
        v-model="annualPlanValues.electric"
        item-name="電力量"
        unit="kWh"
      />
      <AnnualValueInput
        v-model="utilityCostTenThousand"
        item-name="光熱費"
        unit="万円"
      />
      <AnnualValueInput
        v-model="annualPlanValues.co2_emissions"
        item-name="CO₂排出量"
        unit="t-CO₂e"
      />
      <AnnualValueInput
        v-model="carbonCreditValueTenThousand"
        item-name="カーボンクレジット量"
        unit="万円"
      />
      <AnnualValueInput
        v-model="annualPlanValues.electric_reduce"
        item-name="電力削減量"
        unit="kWh"
      />
      <AnnualValueInput
        v-model="utilityCostReduceTenThousand"
        item-name="光熱削減費"
        unit="万円"
      />
      <AnnualValueInput
        v-model="annualPlanValues.co2_emissions_reduce"
        item-name="CO₂削減量"
        unit="t-CO₂e"
      />
      <h2 class="text-lg font-bold mt-6 border-t py-4">設定値</h2>
      <AnnualValueInput
        v-model="annualPlanValues.carbon_credit_price"
        item-name="カーボンクレジット価格"
        unit="円/t-CO₂e"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import AnnualPlanValuesService from '@/services/AnnualPlanValuesService';
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { AnnualPlanValues } from '@/repositories/AnnualPlanValuesRepository';
import AnnualValueInput from '../presenters/AnnualValueInput.vue';
import SubmitButton from '../presenters/SubmitButton.vue';

const screenWidth = ref(window.innerWidth); // "キャンセル"および”保存”ボタンのレスポンシブ
const handleResize = () => {
  screenWidth.value = window.innerWidth;
};

const annualPlanValues = ref<AnnualPlanValues>({
  utility_cost: 0,
  utility_cost_reduce: 0,
  electric: 0,
  electric_reduce: 0,
  co2_emissions: 0,
  co2_emissions_reduce: 0,
  carbon_credit: 0,
  carbon_credit_price: 0,
});

onMounted(async () => {
  const values = await AnnualPlanValuesService.fetchAnnualPlanValues();
  if (values) {
    annualPlanValues.value = values;
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

const isValidAnnualValues = computed(() => {
  const values = Object.values(annualPlanValues.value);
  return values.every((value) => value >= 0 && String(value) !== '');
});

const saveAnnualPlanValues = async () => {
  await AnnualPlanValuesService.updateAnnualPlanValues(annualPlanValues.value);
};

const utilityCostTenThousand = computed({
  get: () => annualPlanValues.value.utility_cost / 10000,
  set: (value) => {
    annualPlanValues.value.utility_cost = value * 10000;
  },
});

const utilityCostReduceTenThousand = computed({
  get: () => annualPlanValues.value.utility_cost_reduce / 10000,
  set: (value) => {
    annualPlanValues.value.utility_cost_reduce = value * 10000;
  },
});

const carbonCreditValueTenThousand = computed({
  get: () => annualPlanValues.value.carbon_credit / 10000,
  set: (value) => {
    annualPlanValues.value.carbon_credit = value * 10000;
  },
});
</script>
