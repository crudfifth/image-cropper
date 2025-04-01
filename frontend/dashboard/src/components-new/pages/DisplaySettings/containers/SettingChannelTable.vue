<template>
  <div class="flex flex-col p-6 bg-white shadow-lg rounded-md">
    <div>
      <div class="flex flex-row justify-between">
        <h2 class="text-right text-2xl font-bold flex items-center mb-4">
          <ListIcon class="mr-3" />
          トレンドグラフ表示設定
        </h2>
        <div class="flex flex-row">
          <button
            id="delete"
            :class="[
              'flex items-center btn-sm text-[12px] font-bold w-32 h-[35px] border-slate-200 hover:border-slate-300 hover:bg-gray-50 rounded shadow-md mr-[32px]',
              selectedChannelIds?.length === 0
                ? 'bg-gray-100 border-gray-100 text-gray-400 cursor-not-allowed'
                : 'hover:bg-gray-300 hover:border-slate-300',
            ]"
            :disabled="selectedChannelIds?.length === 0"
            @click="$emit('delete')"
          >
            <DustboxIcon
              :color="
                selectedChannelIds?.length === 0
                  ? 'text-gray-400'
                  : 'text-red-400'
              "
            />
            削除する
          </button>
          <button
            class="btn-sm text-[12px] font-bold bg-gray-200 hover:bg-gray-300 w-[110px] h-[35px] border-slate-200 hover:border-slate-300 rounded shadow-md mr-[32px]"
            @click="$emit('cancel')"
          >
            キャンセル
          </button>
          <button
            class="btn-sm text-[12px] font-bold w-[110px] h-[35px] border-slate-200 hover:border-slate-300 hover:bg-gray-50 rounded shadow-md"
            :disabled="hasFormError || !dirty"
            :class="{ 'hover:cursor-not-allowed': hasFormError }"
            @click="$emit('save-channels', channels)"
          >
            保存
          </button>
        </div>
      </div>
      <div class="overflow-auto">
        <SettingChannelTableData
          v-if="gateways.length > 0"
          :co2-emissions-factors="co2EmissionsFactors"
          :initial-channels="initialChannels"
          :channels="channels"
          :unit="unit"
          :value-title="valueTitle"
          :gateways="gateways"
          @change-channel-check="$emit('change-channel-check', $event)"
          @update:error="handleError"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import SettingChannelTableData from './SettingChannelTableData.vue';
import { GraphAdapterGateway } from '@/repositories/GraphAdapterRepository';
import { isEqual } from 'lodash-es';
import ListIcon from '@icons/ListIcon.vue';
import DustboxIcon from '@icons/DustboxIcon.vue';
import { Co2EmissionsFactors } from '@/repositories/Co2EmissionsFactorsRepository';

export type Channel = {
  id: number;
  name: string;
  currentdata: number;
  ratio: number;
  selectedGateway: string | null;
  selectedChannel: number;
  formula: string;
  unitPrice: number;
  baseline: number;
  improvementRate: number;
  isCo2EmissionsBaseline: boolean;
};

defineEmits(['save-channels', 'cancel', 'change-channel-check', 'delete']);

const selectedChannelIds = defineModel<number[]>({
  default: [],
});

// propsの定義
const props = defineProps({
  channels: {
    type: Array as () => Channel[],
    required: true,
  },
  initialChannels: {
    type: Array as () => Channel[],
    required: true,
  },
  unit: {
    type: String,
    default: 'kWh',
  },
  valueTitle: {
    type: String,
    default: '電力値',
  },
  gateways: {
    type: Array as () => GraphAdapterGateway[],
    required: true,
  },
  co2EmissionsFactors: {
    type: Array as () => Co2EmissionsFactors,
    required: true,
  },
});

const dirty = computed(() => {
  return !isEqual(props.channels, props.initialChannels);
});

const hasFormError = ref(false);
const handleError = (hasError: boolean) => {
  hasFormError.value = hasError;
};
</script>
