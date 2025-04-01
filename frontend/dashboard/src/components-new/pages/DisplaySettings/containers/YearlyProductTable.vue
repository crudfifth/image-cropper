<template>
  <div
  class="px-2 p-6 overflow-auto flex flex-col bg-white shadow-lg rounded-md"
  >
  <div class="flex flex-col justify-between">
      <div class="flex ml-2 mb-4">
        <MoneyBagIcon class="h-6 mr-2" />
        <span class="text-lg font-bold">原単位設定詳細</span>
      </div>
      <div class="flex h-[40px] mb-4">
        <button
          class="flex items-center justify-center w-1/5 ml-4 rounded bg-white border-2 border-solid-black hover:bg-slate-100 text-slate-500 font-bold"
          :class="{ 'invisible': !adding && checkedDataList.length === 0 }"
          @click="cancelAdding"
          >
          <span class="text-sm">キャンセル</span>
        </button>
        <button
          class="flex items-center justify-center w-1/5 ml-4 rounded text-white font-bold"
          :class="addingClass"
          @click="addEmptyData"
          :disabled="adding || (checkedDataList && checkedDataList.length !== 0)"
        >
          <span>追加</span>
        </button>
        <button
          class="flex items-center justify-center w-1/5 ml-4 text-white bg-blue-500 rounded transition duration-300 font-bold"
          :class="updateClass"
          @click="update"
          :disabled="updateDisabled"
        >
          <span>更新</span>
        </button>
        <button
        id="delete"
          class="flex items-center justify-center w-1/5 ml-4 text-white rounded transition duration-300 font-bold"
          :disabled="checkedDataList.length === 0"
          :class="deleteClass"
          @click="deleteCheckedData"
        >
          <span>削除</span>
        </button>
      </div>
    </div>

    <YearlyProductTable
      :initial-yearly-data="initialYearlyData"
      :yearly-data="yearlyData"
      :checked-data-list="checkedDataList"
      :adding="adding"
      @change-check="handleCheckChange($event)"
      @change-check-all="handleCheckAllChange"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import YearlyProductTable from './YearlyProductTableData.vue';
import EconomicActivityService from '@/services/EconomicActivityService';
import { cloneDeep, isEqual } from 'lodash-es';
import MoneyBagIcon from '@icons/MoneyBagIcon.vue';
import { openAlertModal } from '@/stores/AlertModalStore';

type YearlyData = {
  year: number;
  month: number;
  value: number;
  added?: boolean;
};

const adding = ref(false);
const yearlyData = ref<YearlyData[]>([]);
const checkedDataList = ref<YearlyData[]>([]);
const initialYearlyData = ref<YearlyData[]>([]);

const update = async () => {
  await EconomicActivityService.updateAmounts(yearlyData.value);
  await EconomicActivityService.deleteAmounts(
    initialYearlyData.value.filter(
      (initialData) =>
        !yearlyData.value
          .map((data) => `${data.year}-${data.month}`)
          .includes(`${initialData.year}-${initialData.month}`)
    )
  );
  openAlertModal({ body: '原単位を更新しました' });
  yearlyData.value = yearlyData.value.map((d) => ({ ...d, added: false }));
  initialYearlyData.value = cloneDeep(yearlyData.value);
  adding.value = false;
};

const nextYearMonth = () => {
  if (yearlyData.value.length === 0) {
    return { year: new Date().getFullYear(), month: new Date().getMonth() + 1 };
  }
  const sortedData = yearlyData.value.slice().sort((a, b) => {
    if (a.year === b.year) {
      return a.month - b.month;
    }
    return a.year - b.year;
  });
  const lastData = sortedData[sortedData.length - 1];

  return lastData.month === 12
    ? { year: lastData.year + 1, month: 1 }
    : { year: lastData.year, month: lastData.month + 1 };
};

const addEmptyData = () => {
  adding.value = true;
  const newYearlyData: YearlyData = {
    ...nextYearMonth(),
    value: 0,
    added: true,
  };
  yearlyData.value.push(newYearlyData);
};

const cancelAdding = () => {
  if (adding.value) {
    yearlyData.value = yearlyData.value.filter(data => !data.added);
    adding.value = false;
  }
  checkedDataList.value = [];
};

const updateDisabled = computed(() => {
  return checkedDataList.value.length === 0 && !adding.value || !isValidInputs.value || !dirtyInputs.value;
});

const addingClass = computed(() => {
  return {
    'cursor-not-allowed bg-slate-300 hover:bg-slate-300': adding.value || (checkedDataList.value && checkedDataList.value.length !== 0),
    'bg-green-600 hover:bg-green-700': !adding.value && (!checkedDataList.value || checkedDataList.value.length === 0),
  }
});

const updateClass = computed(() => {
  if (adding.value || checkedDataList.value.length > 0) {
    return ['hover:bg-blue-600 hover:border-slate-300']; 
  } else {
    return ['cursor-not-allowed bg-slate-300 hover:bg-slate-300']; 
  }
});
const deleteClass = computed(() => {
  return [
    'flex items-center justify-center text-white px-4 rounded transition duration-300 font-bold',
    checkedDataList.value.length === 0 ? 'cursor-not-allowed bg-slate-300 hover:bg-slate-300' : 'bg-red-500 hover:bg-red-600 hover:border-slate-300'
  ];
});

const handleCheckChange = async ({
  event,
  data,
}: {
  event: Event;
  data: YearlyData;
}) => {
  const checked = (event.target as HTMLInputElement).checked;
  if (checked) {
    checkedDataList.value.push(data);
  } else {
    checkedDataList.value = checkedDataList.value.filter((d) => d !== data);
  }
};

const deleteCheckedData = async () => {
  await EconomicActivityService.deleteAmounts(
    checkedDataList.value.filter((d) => !d.added)
  );
  openAlertModal({
    body: '原単位を削除しました',
  });
  yearlyData.value = yearlyData.value.filter(
    (d) => !checkedDataList.value.includes(d)
  );
  checkedDataList.value = [];
  initialYearlyData.value = cloneDeep(yearlyData.value);
  adding.value = false;
};

const handleCheckAllChange = async (event: Event) => {
  const checked = (event.target as HTMLInputElement).checked;
  if (checked) {
    checkedDataList.value = yearlyData.value;
  } else {
    checkedDataList.value = [];
  }
};

const isValidInputs = computed(() => {
  return yearlyData.value.every((d) => d.value >= 0);
});

const dirtyInputs = computed(() => {
  return !isEqual(yearlyData.value, initialYearlyData.value);
});


onMounted(async () => {
  yearlyData.value = await EconomicActivityService.fetchAmounts();
  initialYearlyData.value = cloneDeep(yearlyData.value);
});
</script>
