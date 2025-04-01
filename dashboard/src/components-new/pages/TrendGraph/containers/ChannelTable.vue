<template>
  <div class="flex flex-wrap -mx-2">
    <!-- LeftSideTable -->
    <div class="w-1/2 px-2">
      <GraphTablePane
        v-model="checkboxStatesLeft"
        :channels="graphDataArray.slice(0, 8)"
        :unit="unitLabelText"
        :value-title="valueTitleText"
        :value-round-function="valueRoundFunction"
      />
    </div>
    <!-- RightSideTable -->
    <div class="w-1/2 px-2">
      <GraphTablePane
        v-model="checkboxStatesRight"
        :channels="graphDataArray.slice(8, 16)"
        :unit="unitLabelText"
        :value-title="valueTitleText"
        :value-round-function="valueRoundFunction"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { match } from 'ts-pattern';
import { createGraphUnitLabelText } from '@/utils/EnergyTypeUtils';
import { roundTwoDecimal } from '@/utils/Round';
import GraphTablePane from './GraphTablePane.vue';
import type { GraphKeyType } from '@/services/GraphService';

import type { GraphTableValueType } from './ChannelListSectionLayout.vue';
import { graphStateStore } from '@/stores/TrendGraphStore';

const props = defineProps<{
  graphTableData: GraphTableValueType[];
}>();

const graphDataArray = computed(() => {
  return props.graphTableData;
});

// const unitLabelText = computed(() =>
//   createGraphUnitLabelText({ graphType: graphStateStore.graphType })
// );
const isKgUnit = true;
const unitLabelText = computed(() =>
  createGraphUnitLabelText({
     graphType: graphStateStore.graphType,
     isKgUnit: isKgUnit
  })
);

const valueTitleText = computed(() =>
  match(graphStateStore.graphType)
    .with('electricity', () => '電力量')
    .with('utilityCost', () => '光熱費')
    .with('co2Emission', () => 'CO₂排出量')
    .with('carbonCredit', () => 'CC量')
    .with('electricityReduction', () => '電力削減量')
    .with('utilityCostReduction', () => '光熱費削減量')
    .with('co2EmissionReduction', () => 'CO₂削減量')
    .with('carbonFootprint', () => '電力量')
    .exhaustive()
);

const valueRoundFunction = computed(() =>
  match(graphStateStore.graphType)
    .with('electricity', () => roundTwoDecimal)
    .with('utilityCost', () => Math.round)
    .with('co2Emission', () => roundTwoDecimal)
    .with('carbonCredit', () => Math.round)
    .with('electricityReduction', () => roundTwoDecimal)
    .with('utilityCostReduction', () => roundTwoDecimal)
    .with('co2EmissionReduction', () => roundTwoDecimal)
    .with('carbonFootprint', () => roundTwoDecimal)
    .exhaustive()
);

const checkboxStatesLeft = ref<boolean[]>(Array(8).fill(false));
const checkboxStatesRight = ref<boolean[]>(Array(8).fill(false));

// チャンネルの選択状態の初期値を設定する。
// disabledなチャンネルは選択しない。
// TODO: トレンドグラフ表示中に、他のユーザーにチャンネルの設定を変えられてしまった時に対処する。disabledなチャンネルの状態が変わる可能性がある。
watch(
  graphDataArray,
  () => {
    checkboxStatesLeft.value = graphDataArray.value
      .slice(0, 8)
      .map((x) => x.isEnabled);
    checkboxStatesRight.value = graphDataArray.value
      .slice(8, 16)
      .map((x) => x.isEnabled);
  },
  { once: true }
);

watch(checkboxStatesLeft, () => {
  updateSelectedGraphs();
});

watch(checkboxStatesRight, () => {
  updateSelectedGraphs();
});

const updateSelectedGraphs = () => {
  const leftVals = checkboxStatesLeft.value
    .map((value, index) => {
      return value ? (index + 1).toString() : '';
    })
    .filter((x) => x !== '')
    .map((x) => x as GraphKeyType);

  const rightVals = checkboxStatesRight.value
    .map((value, index) => {
      return value ? (index + 9).toString() : '';
    })
    .filter((x) => x !== '')
    .map((x) => x as GraphKeyType);

  graphStateStore.selectedGraphKeys = [...leftVals, ...rightVals];
};
</script>
