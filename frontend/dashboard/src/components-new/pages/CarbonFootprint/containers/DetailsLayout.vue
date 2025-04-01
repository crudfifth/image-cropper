<template>
  <div class="bg-white shadow-lg rounded-md py-8 px-10">
    <div class="flex justify-between items-center">
      <div class="flex items-center ml-4 mb-2">
        <ListIcon class="mr-2" />
        <div class="text-2xl font-bold">詳細一覧</div>
      </div>
      <div class="flex items-center mb-2 mr-8">
        <button
          v-if="adding || checkedFootprintId"
          class="mr-2 flex items-center justify-center px-4 rounded bg-white border-2 border-solid-black hover:bg-slate-100 text-slate-500 py-2 font-bold"
          @click="cancelAdd"
        >
          キャンセル
        </button>
        <AddButton
          class="mr-2"
          :class="{
            'opacity-50 cursor-not-allowed':
              checkedFootprintId !== undefined || adding,
          }"
          :on-click-async="onClickAdd"
          :disabled="checkedFootprintId !== undefined || adding"
        />
        <SubmitButton
          class="mr-2"
          :on-click-async="updateFootprint"
          :disabled="
            (!adding && checkedFootprintId === undefined) ||
            (checkedFootprintId !== undefined && !validEditingFootprint)
          "
        />
        <DeleteButton
          class="mr-2"
          :on-click-async="deleteFootprint"
          :disabled="checkedFootprintId === undefined"
        />
      </div>
    </div>
    <div class="flex flex-col mb-4 overflow-auto whitespace-nowrap h-[348px]">
      <table class="border-separate border-spacing-x-4">
        <thead class="text-center text-sm sticky top-0 bg-white z-10">
          <tr>
            <th rowspan="2">チェック</th>
            <th class="border-b-2 border-gray-300 p-6 w-[190px]" rowspan="2">
              グループ名称
            </th>
            <th class="border-b-2 border-gray-300 w-[205px]" rowspan="2">
              チャンネル名（グラフ内訳）
            </th>
            <th class="border-b-2 border-gray-300" colspan="2">取得日時</th>
            <th class="border-b-2 border-gray-300" rowspan="2">
              電力量<br />[kWh]
            </th>
            <th class="border-b-2 border-gray-300 w-[130px]" rowspan="2">
              CO₂排出量<br />[t-CO₂e]
            </th>
            <th class="border-b-2 border-gray-300 w-[110px]" rowspan="2">
              Scope区分
            </th>
          </tr>
          <tr>
            <th class="border-b-2 border-gray-300">開始点</th>
            <th class="border-b-2 border-gray-300">終点</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="adding">
            <td></td>
            <td class="border-b-2 boder-gray-200 p-4">
              <input
                v-model="addingFootprint.process_name"
                class="form-input w-[140px]"
                :class="{
                  'border-2 border-red-500': !validateField(
                    addingFootprint,
                    'process_name'
                  ),
                }"
                type="text"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <input
                v-model="addingFootprint.channel_name"
                class="form-input w-[140px]"
                :class="{
                  'border-2 border-red-500': !validateField(
                    addingFootprint,
                    'channel_name'
                  ),
                }"
                type="text"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <div class="w-60">
                <span class="flex justify-center">-</span>
              </div>
            </td>
            <td class="border-b-2 boder-gray-200">
              <div class="w-60">
                <span class="flex justify-center">-</span>
              </div>
            </td>
            <td class="border-b-2 boder-gray-200">
              <span class="flex justify-center">-</span>
            </td>
            <td class="border-b-2 boder-gray-200">
              <NonNegativeNumberInput
                v-model="addingFootprint.co2_emissions"
                class="form-input w-[140px]"
                :class="{
                  'border-2 border-red-500': !validateField(
                    addingFootprint,
                    'co2_emissions'
                  ),
                }"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <select
                v-model="addingFootprint.scope_no"
                class="form-select w-[140px]"
              >
                <option value="1">Scope1</option>
                <option value="2">Scope2</option>
                <option value="3">Scope3</option>
              </select>
            </td>
          </tr>
          <tr
            v-for="footprint in carbonFootprint"
            :key="footprint.id"
            class="text-center font-medium text-md"
          >
            <td>
              <input
                class="form-checkbox"
                :class="{ 'bg-gray-200': adding, 'opacity-70': adding }"
                type="checkbox"
                :checked="checkedFootprintId === footprint.id"
                :disabled="adding"
                @change="onChangeCheck($event, footprint)"
              />
            </td>
            <td
              class="border-b-2 border-gray-200 h-[60px]"
              :class="{ 'p-4': checkedFootprintId !== footprint.id }"
            >
              <span v-if="checkedFootprintId !== footprint.id">{{
                footprint.process_name
              }}</span>
              <input
                v-else
                v-model="footprint.process_name"
                class="form-input w-full"
                :class="{
                  'border-2 border-red-500': !validateField(
                    footprint,
                    'process_name'
                  ),
                }"
                type="text"
              />
            </td>
            <td
              class="border-b-2 border-gray-200"
              :class="{ 'p-4': checkedFootprintId !== footprint.id }"
            >
              <span v-if="checkedFootprintId !== footprint.id">{{
                footprint.channel_name
              }}</span>
              <input
                v-else
                v-model="footprint.channel_name"
                class="form-input w-full"
                :class="{
                  'border-2 border-red-500': !validateField(
                    footprint,
                    'channel_name'
                  ),
                }"
                type="text"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <span>{{
                footprint.start_date
                  ? formatDateTime(footprint.start_date)
                  : '-'
              }}</span>
            </td>
            <td class="border-b-2 boder-gray-200">
              <span>{{
                footprint.end_date ? formatDateTime(footprint.end_date) : '-'
              }}</span>
            </td>
            <td class="border-b-2 boder-gray-200">
              <span>{{ footprint.electric_value.toLocaleString() }}</span>
            </td>
            <td class="border-b-2 boder-gray-200">
              <NonNegativeNumberInput
                v-if="!adding && (checkedFootprintId === footprint.id && !(footprint.start_date || footprint.end_date))"
                v-model="footprint.co2_emissions"
                class="form-input w-full"
                :class="{
                  'border-2 border-red-500': !validateField(
                    footprint,
                    'co2_emissions'
                  ),
                }"
              />
              <span v-else>
                {{ footprint.co2_emissions.toLocaleString() }}
              </span>
            </td>
            <td class="border-b-2 boder-gray-200">
              <span v-if="checkedFootprintId !== footprint.id"
                >Scope{{ footprint.scope_no }}</span
              >
              <select
                v-else
                v-model="footprint.scope_no"
                class="form-select w-full"
              >
                <option value="1">Scope1</option>
                <option value="2">Scope2</option>
                <option value="3">Scope3</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CarbonFootprint } from '@/repositories/CarbonFootprintRepository';
import CarbonFootprintService from '@/services/CarbonFootprintService';
import { PropType, computed, ref, watch } from 'vue';
import ListIcon from '@icons/ListIcon.vue';
import AddButton from '../presenters/AddButton.vue';
import SubmitButton from '../presenters/SubmitButton.vue';
import DeleteButton from '../presenters/DeleteButton.vue';
import NonNegativeNumberInput from '@inputs/NonNegativeNumberInput.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import { openConfirmModal } from '@/stores/ConfirmModalStore';

const props = defineProps({
  carbonFootprint: {
    type: Array as PropType<CarbonFootprint[]>,
    required: true,
  },
});

const emit = defineEmits([
  'delete-carbon-footprint',
  'add-carbon-footprint',
  'update-carbon-footprint',
]);

const formatDateTime = (date: string | null | undefined) => {
  if (date == null) {
    return undefined;
  }
  const d = new Date(date);
  const month = ('0' + (d.getMonth() + 1)).slice(-2);
  const day = ('0' + d.getDate()).slice(-2);
  const hour = ('0' + d.getHours()).slice(-2);
  const minute = ('0' + d.getMinutes()).slice(-2);
  return `${d.getFullYear()}/${month}/${day} ${hour}:${minute}`;
};

const checkedFootprintId = ref<string | undefined>(undefined);

const onChangeCheck = (e: Event, footprint: CarbonFootprint) => {
  checkedFootprintId.value = (e.target as HTMLInputElement).checked
    ? footprint.id
    : undefined;
};

const cancelAdd = () => {
  adding.value = false; 
  addingFootprint.value = {
    process_name: '',
    channel_name: '',
    start_date: undefined,
    end_date: undefined,
    electric_value: 0,
    co2_emissions: 0,
    scope_no: 1,
  };
  checkedFootprintId.value = undefined;
};

const updateFootprint = async () => {
  if (adding.value) {
    const createdFootprint = await CarbonFootprintService.createCarbonFootprint(
      addingFootprint.value
    );
    emit('add-carbon-footprint', createdFootprint);
  }
  const footprint = props.carbonFootprint.find(
    (f) => f.id === checkedFootprintId.value
  );
  if (footprint) {
    await CarbonFootprintService.updateCarbonFootprint(footprint);
  }
  if (adding.value || footprint) {
    emit('update-carbon-footprint');
  }
  adding.value = false;
  addingFootprint.value = {
    process_name: '',
    channel_name: '',
    start_date: undefined,
    end_date: undefined,
    electric_value: 0,
    co2_emissions: 0,
    scope_no: 1,
  };
  checkedFootprintId.value = undefined;
};

const deleteFootprint = async () => {
  openConfirmModal({
    body: '削除しますか？',
    onResponse: async (confirmed: boolean) => {
      if (confirmed && checkedFootprintId.value) {
        await CarbonFootprintService.deleteCarbonFootprint(
          checkedFootprintId.value
        );
        emit('delete-carbon-footprint', checkedFootprintId.value);
        checkedFootprintId.value = undefined;
        emit('update-carbon-footprint');
      }
    },
  });
};

const adding = ref(false);
const addingFootprint = ref<Omit<CarbonFootprint, 'id'>>({
  process_name: '',
  channel_name: '',
  start_date: undefined,
  end_date: undefined,
  electric_value: 0,
  co2_emissions: 0,
  scope_no: 1,
});

const onClickAdd = async () => {
  adding.value = true;
};

const validateField = (
  footprint: Omit<CarbonFootprint, 'id' | 'start_date' | 'end_date' | 'scope'>,
  field: keyof Omit<CarbonFootprint, 'id' | 'start_date' | 'end_date' | 'scope'>
) => {
  if (String(footprint[field]) === '') {
    return false;
  }
  if (field === 'electric_value' || field === 'co2_emissions') {
    return footprint[field] >= 0;
  }
  return true;
};

const validAddingFootprint = computed(() => {
  if (!adding.value) {
    return true;
  }
  return (
    validateField(addingFootprint.value, 'process_name') &&
    validateField(addingFootprint.value, 'channel_name') &&
    validateField(addingFootprint.value, 'electric_value') &&
    validateField(addingFootprint.value, 'co2_emissions')
  );
});

const validEditingFootprint = computed(() => {
  const footprint = props.carbonFootprint.find(
    (f) => f.id === checkedFootprintId.value
  );
  if (footprint) {
    return (
      validateField(footprint, 'process_name') &&
      validateField(footprint, 'channel_name') &&
      validateField(footprint, 'electric_value') &&
      validateField(footprint, 'co2_emissions')
    );
  }
  return false;
});

// watch(addingFootprint.value, (newValue, oldValue) => {
//   if (newValue.co2_emissions < 0) {
//     addingFootprint.value.co2_emissions = 0;
//   }
// }, { deep: true });

props.carbonFootprint.forEach((footprint) => {
  watch(
    () => footprint.co2_emissions,
    (newValue, oldValue) => {
      if (newValue < 0) {
        footprint.co2_emissions = 0;
      }
    }
  );
});
</script>
