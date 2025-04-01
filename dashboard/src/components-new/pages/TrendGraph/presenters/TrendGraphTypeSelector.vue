<template>
  <select
    id="grid-state"
    v-model="localValue"
    class="block text-sm appearance-none col-3 bg-white border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
  >
    <option
      v-for="[type, label] in Array.from(labels)"
      :key="type"
      :value="type"
    >
      {{ label }}
    </option>
  </select>
</template>

<script setup lang="ts">
import { TrendGraphType } from '@/types';

const labels = new Map<TrendGraphType, string>([
  ['electricity', '電力量'],
  ['utilityCost', '光熱費'],
  ['co2Emission', 'CO₂排出量'],
  ['carbonCredit', 'カーボンクレジット量'],
  ['electricityReduction', '電力削減量'],
  ['utilityCostReduction', '光熱削減費'],
  ['co2EmissionReduction', 'CO₂削減量'],
  ['carbonFootprint', 'カーボンフットプリント'],
]);

const localValue = defineModel<TrendGraphType>();
</script>
