<template>
  <table class="text-sm table-auto text-center border-b-2 min-w-full">
    <thead class="bg-neutral-200 divide-x divide-white">
      <tr class="[&>th]:p-1">
        <th class="bg-white">
          <input
            class="form-checkbox"
            :class="{ 'bg-gray-200': adding, 'opacity-70': adding }"
            type="checkbox"
            :checked="checkedDataList.length === yearlyData.length"
            @change="$emit('change-check-all', $event)"
            :disabled="adding"
          />
        </th>
        <th class="bg-white" style="width: 4px"></th>
        <th>年月</th>
        <th class="bg-white" style="width: 4px"></th>
        <th>原単位<br />ex生産個数</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-300 [&>td]:p-1">
      <tr
        v-for="(data, index) in yearlyData"
        :key="index"
        class="text-gray-700"
      >
        <td>
          <input
            v-if="!data.added"
            type="checkbox"
            class="form-checkbox"
            :class="{ 'bg-gray-200': adding, 'opacity-70': adding }"
            :checked="checkedDataList.includes(data)"
            @change="$emit('change-check', { event: $event, data })"
            :disabled="adding"
          />
        </td>
        <td></td>
        <td class="px-4 py-1">
          <div>
            <input
              v-model="data.year"
              class="form-input w-[80px] my-1 mr-1"
              type="number"
              :class="{
                'border-2 border-blue-200': dirtyField(index, data, 'year'),
              }"
            />年<select
              v-model.number="data.month"
              class="form-select ml-1 mr-1"
              :class="{
                'border-2 border-blue-200': dirtyField(index, data, 'month'),
              }"
            >
              <option
                v-for="month in selectableMonths(data)"
                :key="month"
                :value="month"
              >
                {{ month }}
              </option></select
            >月
          </div>
        </td>
        <td></td>
        <td class="px-4 py-1">
          <input
            v-model="data.value"
            class="form-input w-[80px]"
            type="number"
            :class="{
              'border-2 border-red-500': data.value < 0,
              'border-2 border-blue-200': dirtyField(index, data, 'value'),
            }"
          />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { PropType } from 'vue';

type YearlyData = {
  year: number;
  month: number;
  value: number;
  added?: boolean;
};

const props = defineProps({
  yearlyData: {
    type: Array as PropType<YearlyData[]>,
    required: true,
  },
  initialYearlyData: {
    type: Array as PropType<YearlyData[]>,
    required: true,
  },
  checkedDataList: {
    type: Array as PropType<YearlyData[]>,
    required: true,
  },
  adding: Boolean,
});

defineEmits(['change-check', 'change-check-all']);

const selectableMonths = (data: YearlyData) => {
  const allMonth = Array.from({ length: 12 }, (_, i) => i + 1);
  const usedMonth = props.yearlyData
    .filter((d) => d.year === data.year)
    .map((d) => d.month);
  return [
    data.month,
    ...allMonth.filter((month) => !usedMonth.includes(month)),
  ];
};

const dirtyField = (
  index: number,
  data: YearlyData,
  field: keyof YearlyData
) => {
  const initialData = props.initialYearlyData[index];
  return initialData ? initialData[field] !== data[field] : true;
};
</script>
