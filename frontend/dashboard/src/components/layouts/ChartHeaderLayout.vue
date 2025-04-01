<!-- TODO: 旧ダッシュボードで使われていた共有コンポーネント。削除しても良いかもしれない -->
<template>
  <div class="flex justify-between gap-2 items-end pb-4 w-full">
    <h2 class="text-2xl font-bold">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="22"
        viewBox="0 0 18 22"
        class="inline mr-3 mb-1"
      >
        <g transform="translate(-41.781 -0.001)">
          <path
            d="M59.559,11.671c-1.211-4.939-5.9-6.8-6.312-7.248L54.4.129a5.18,5.18,0,0,0-3.46.411c-2.569,1.128-4-.31-4-.31L48.209,4.49c-.4.463-5.386,2.537-6.289,7.417C41.14,16.1,43.579,22.1,50.865,22S60.578,15.818,59.559,11.671Zm-5.355.421v1.171H51.846l-.393.626v.747H54.2v1.172H51.453v2.04H50.11v-2.04H47.358V14.636H50.11v-.747l-.394-.626H47.358V12.092h1.621L47.05,9.022h1.375l2.356,3.749,2.357-3.749h1.374l-1.929,3.07Z"
            transform="translate(0 0)"
            fill="#005da8"
          />
        </g>
      </svg>
      {{ chartHeader }}
    </h2>

    <div class="flex flex-col gap-2">
      <div class="flex justify-end items-center gap-2">
        <div
          v-if="amountUnitLabelValues && amountUnitLabelValues.length > 0"
          class="flex justify-between gap-2 border bg-gray-50 rounded px-2 py-1"
        >
          <label
            v-for="(unit, index) in amountUnitLabelValues"
            :key="index"
            :value="unit"
            class="cursor-pointer text-center"
          >
            <input
              v-model="selectedAmountUnit"
              type="radio"
              name="radioType"
              class="peer sr-only"
              :value="unit.value"
              @change="updateAmountUnit"
            />
            <div
              class="text-zinc-300 peer-checked:text-main-blue peer-checked:bg-white drop-shadow-md rounded px-2 py-1"
              aria-hidden="true"
            >
              {{ unit.label }}
            </div>
          </label>
        </div>

        <div
          class="flex justify-between gap-2 border bg-gray-50 rounded px-2 py-1"
        >
          <label
            v-for="(intens, index) in intensitiyLabelValues"
            :key="index"
            class="cursor-pointer text-center"
          >
            <input
              v-model="selectedIntensity"
              type="radio"
              name="radio-unit"
              class="peer sr-only"
              :value="intens.value"
              @change="updateIntensity"
            />
            <div
              class="text-zinc-300 peer-checked:text-main-blue peer-checked:bg-white drop-shadow-md rounded px-2 py-1"
              aria-hidden="true"
            >
              {{ intens.label }}
            </div>
          </label>
        </div>
        <div
          class="flex justify-between gap-2 border bg-gray-50 rounded px-2 py-1"
        >
          <label
            v-for="(period, index) in timePeriodLabelValues"
            :key="index"
            class="cursor-pointer text-center"
          >
            <input
              v-model="selectedTimePeriod"
              type="radio"
              name="radio-range"
              class="peer sr-only"
              :value="period.value"
              @change="updateTimePeriod"
            />
            <div
              class="text-zinc-300 peer-checked:text-main-blue peer-checked:bg-white drop-shadow-md rounded px-2 py-1"
              aria-hidden="true"
            >
              {{ period.label }}
            </div>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import type { PropType, Ref } from 'vue';
import type { IntensityType, TimePeriodType } from '@/types';

const props = defineProps({
  chartHeader: {
    type: String,
    required: true,
  },
  onChange: {
    type: Function as PropType<(payload: Event) => void>,
    required: true,
  },
  amountUnitLabelValues: {
    type: Array as PropType<{ label: string; value: string }[]>,
    required: false,
    default: () => [
      { label: '円', value: 'yen' },
      { label: 'kWh', value: 'kwh' },
    ],
  },
  amountUnit: {
    type: String,
    required: true,
  },
  intensity: {
    type: String as PropType<IntensityType>,
    required: true,
  },
  timePeriod: {
    type: String as PropType<TimePeriodType>,
    required: true,
  },
  onChangeEconomicActivity: {
    type: Function as PropType<(payload: Event) => void>,
    required: true,
  },
  economicActivity: {
    type: Object as PropType<{ id: string; name: string } | undefined>,
    required: true,
  },
  economicActivities: {
    type: Array as PropType<{ id: string; name: string }[]>,
    required: true,
  },
});

const emit = defineEmits([
  'update:amountUnit',
  'update:intensity',
  'update:timePeriod',
  'update:economicActivity',
  'update:entityId',
]);

const timePeriodLabelValues = [
  { label: '日', value: 'day' as const },
  { label: '週', value: 'week' as const },
  { label: '月', value: 'month' as const },
  { label: '年', value: 'year' as const },
];

const intensitiyLabelValues = [
  { label: '標準', value: 'default' as const },
  { label: '原単位', value: 'intensity' as const },
];

const selectedAmountUnit = ref(props.amountUnit);
const selectedIntensity = ref(props.intensity);
const selectedTimePeriod = ref(props.timePeriod);
const selectedEconomicActivity = ref(props.economicActivity?.id);

const updateAmountUnit = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target) {
    selectedAmountUnit.value = target.value;
    emit('update:amountUnit', target.value);
    props.onChange(event);
  }
};

const updateIntensity = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target) {
    selectedIntensity.value = target.value as IntensityType;
    emit('update:intensity', target.value);
    props.onChange(event);
  }
};

const updateTimePeriod = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target) {
    selectedTimePeriod.value = target.value as TimePeriodType;
    emit('update:timePeriod', target.value);
    props.onChange(event);
  }
};

watch(
  () => props.economicActivity,
  (newVal) => {
    selectedEconomicActivity.value = newVal?.id;
  }
);
</script>
