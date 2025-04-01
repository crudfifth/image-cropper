<template>
  <table class="text-base table-auto text-left border-b-2 min-w-full">
    <thead class="text-sm table-auto text-left border-b-2 min-w-full">
      <tr class="[&>th]:text-sm px-4 py-2">
        <th rowspan="2" class="px-4 py-2">
          <div class="w-14 flex justify-around">
            <input
              v-model="isAllChecked"
              type="checkbox"
              class="form-checkbox h-5 w-5 text-gray-600"
              @change="toggleAll"
            /><span class="ml-3">#</span>
          </div>
        </th>
        <th rowspan="2">チャンネル名（グラフ内訳）</th>
        <th rowspan="2">ゲートウェイ名</th>
        <th rowspan="2">取得元CH</th>
        <th rowspan="2" class="px-4">計算式</th>
        <th rowspan="2" class="px-4">光熱費単価</th>
        <th colspan="1" class="text-right border-b-2">CO₂排出係数</th>
        <th colspan="1" class="text-left border-b-2">t-CO₂/kWh</th>
        <th rowspan="2" class="px-4">改善割合</th>
      </tr>
      <tr class="[&>th]:text-center">
        <th>現状</th>
        <th>ベースライン</th>
      </tr>
    </thead>
    <tbody class="divide-y">
      <tr v-for="channel in channels" :key="channel.id" class="text-gray-700">
        <td class="px-4 py-2">
          <div class="flex justify-around">
            <input
              :id="'checkbox-' + channel.id"
              :checked="selectedChannelIds.includes(channel.id)"
              type="checkbox"
              class="form-checkbox h-5 w-5 text-gray-600"
              @change="
                handleCheckChange(
                  channel.id,
                  (<HTMLInputElement>$event.target)?.checked
                )
              "
            /><span class="ml-2">{{ channel.id }}</span>
          </div>
        </td>
        <td class="py-2">
          <input
            :id="'name-' + channel.id"
            v-model="channel.name"
            type="text"
            class="form-input rounded-md border-2"
            :class="{
              'border-2 border-blue-200': dirtyChannelField(channel, 'name'),
            }"
            @input="validateChannels"
          />
        </td>
        <td class="py-2">
          <select
            v-model="channel.selectedGateway"
            class="form-input rounded-md text-gray-700 pl-3 pr-10"
            :class="{
              'border-2 border-blue-200': dirtyChannelField(
                channel,
                'selectedGateway'
              ),
            }"
            @change="validateChannels"
          >
            <option
              v-for="gateway in gateways"
              :key="gateway.name"
              :value="gateway.gateway_id"
            >
              {{ gateway.name }}
            </option>
          </select>
        </td>
        <td class="py-2">
          <select
            v-model="channel.selectedChannel"
            class="form-input rounded-md text-gray-700 pl-3 pr-10 w-[200px]"
            :class="{
              'border-2 border-blue-200': dirtyChannelField(
                channel,
                'selectedChannel'
              ),
            }"
            @change="validateChannels"
          >
            <option
              v-for="device in selectedGatewayObj(channel.id)?.device_names ||
              []"
              :key="device[0]"
              :value="device[0]"
              :selected="device[0] === channel.selectedChannel"
            >
              {{ device[1] }}
            </option>
          </select>
        </td>
        <td class="px-4 py-2">
          <FormulaInput
            v-model="channel.formula"
            :dirty="dirtyChannelField(channel, 'formula')"
            @update:error="(hasError:boolean) => handleFormulaError(hasError, channel.id)"
          />
        </td>
        <td class="px-4 py-2">
          <div class="flex items-center">
            <input
              v-model="channel.unitPrice"
              class="form-input w-24 mr-2"
              type="number"
              :class="{
                'border-2 border-red-500':
                  channel.unitPrice === '' || channel.unitPrice < 0,
                'border-2 border-blue-200': dirtyChannelField(
                  channel,
                  'unitPrice'
                ),
              }"
              @input="validateChannels"
            />
            <span class="text-xs">円/kWh</span>
          </div>
          <span v-if="channel.unitPrice === ''" class="text-sm text-red-500">
            入力は必須です
          </span>
          <span v-else-if="channel.unitPrice < 0" class="text-sm text-red-500">
            正の値を入力してください
          </span>
        </td>
        <td class="py-2 relative">
          <ComboInput
            v-model="channel.currentdata"
            :options="co2EmissionsFactors.map(factor => ({
              id: factor.no,
              value: factor.factor,
              text: factor.region_name ? `[${factor.region_name}] ${factor.factor}` : factor.factor
            }))"
            :isDisabled="false"
            :additionalDisabledCondition="false"
            :dirtyField="() => dirtyChannelField(channel, 'currentdata')"
            @validateChannels="validateChannels"
          />
        </td>
        <td class="py-2 pl-2 relative">
          <ComboInput
            v-model="channel.baseline"
            :options="co2EmissionsFactors.map(factor => ({
              id: factor.no,
              value: factor.factor,
              text: factor.region_name ? `[${factor.region_name}] ${factor.factor}` : factor.factor
            }))"
            :isDisabled="!channel.isCo2EmissionsBaseline"
            :additionalDisabledCondition="false"
            :dirtyField="() => dirtyChannelField(channel, 'baseline')"
            @validateChannels="validateChannels"
          />
        </td>
        <td class="px-4 py-2">
          <div class="flex items-center">
            <label class="inline-flex items-center cursor-pointer mr-8">
              <input
                :checked="!channel.isCo2EmissionsBaseline"
                type="checkbox"
                class="sr-only sm:not-sr-only peer"
                @input="
                  ($event) => handleBaselineToggle(($event.target as HTMLInputElement)?.checked, channel)
                "
              />
              <div
                class="relative w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
              ></div>
            </label>
            <div class="relative w-24">
              <input
                :id="'name-' + channel.improvementRate"
                v-model.number="channel.improvementRate"
                type="number"
                class="form-input rounded-md w-full pr-10"
                min="0"
                step="1"
                :class="{
                  'border-2 border-red-500':
                    channel.improvementRate === '' ||
                    channel.improvementRate < 0,
                  'text-gray-400': channel.isCo2EmissionsBaseline,
                  'border-2 border-blue-200': dirtyChannelField(
                    channel,
                    'improvementRate'
                  ),
                }"
                :disabled="channel.isCo2EmissionsBaseline"
                @input="validateChannels"
              />
              <span
                class="absolute inset-y-0 right-2 flex items-center"
                :class="{ 'text-gray-400': channel.isCo2EmissionsBaseline }"
              >
                %
              </span>
            </div>
          </div>
          <span
            v-if="channel.improvementRate === ''"
            class="text-sm text-red-500"
          >
            入力は必須です
          </span>
          <span
            v-else-if="channel.improvementRate < 0"
            class="text-sm text-red-500"
          >
            正の値を入力してください
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue';
import { GraphAdapterGateway } from '@/repositories/GraphAdapterRepository';
import { Co2EmissionsFactors } from '@/repositories/Co2EmissionsFactorsRepository';
import FormulaInput from '../presenters/FormulaInput.vue';
import ComboInput from '@inputs/ComboInput.vue';

export type Channel = {
  id: number;
  name: string;
  currentdata: number | '';
  selectedGateway: string | null;
  selectedChannel: number;
  formula: string;
  unitPrice: number | '';
  baseline: number | '';
  improvementRate: number | '';
  isCo2EmissionsBaseline: boolean;
};
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

const emits = defineEmits(['change-channel-check', 'update:error']);
const selectedChannelIds = ref<number[]>([]);
const isAllChecked = ref<boolean>(false);

const toggleAll = () => {
  if (selectedChannelIds.value.length === props.channels.length) {
    selectedChannelIds.value = [];
  } else {
    selectedChannelIds.value = props.channels.map((channel) => channel.id);
  }
};

const handleCheckChange = (channelId: number, checked: boolean) => {
  if (checked && !selectedChannelIds.value.includes(channelId)) {
    selectedChannelIds.value.push(channelId);
    if (selectedChannelIds.value.length === props.channels.length) {
      isAllChecked.value = true;
    }
  } else if (!checked && selectedChannelIds.value.includes(channelId)) {
    const index = selectedChannelIds.value.indexOf(channelId);
    selectedChannelIds.value.splice(index, 1);
    isAllChecked.value = false;
  }
};

const selectedGatewayObj = (channelId: number) => {
  const channel = props.channels.find((channel) => channel.id === channelId);
  if (channel) {
    return props.gateways.find(
      (gateway) => gateway.gateway_id === channel.selectedGateway
    );
  }
  return undefined;
};

const formulaErrorChannelIds = ref<number[]>([]);

const handleFormulaError = (hasError: boolean, channelId: number) => {
  if (hasError && !formulaErrorChannelIds.value.includes(channelId)) {
    formulaErrorChannelIds.value.push(channelId);
  } else if (!hasError && formulaErrorChannelIds.value.includes(channelId)) {
    const index = formulaErrorChannelIds.value.indexOf(channelId);
    formulaErrorChannelIds.value.splice(index, 1);
  }
  validateChannels();
};

const validateChannels = () => {
  const hasError =
    formulaErrorChannelIds.value.length > 0 ||
    props.channels.some((channel) => {
      return (
        channel.unitPrice === '' ||
        channel.unitPrice < 0 ||
        channel.improvementRate === '' ||
        channel.improvementRate < 0 ||
        (!channel.currentdata && channel.selectedChannel)
      );
    });
  console.log(`hasError: ${hasError}`);
  emits('update:error', hasError);
};

watch(
  () => selectedChannelIds.value.length,
  () => {
    emits('change-channel-check', selectedChannelIds.value);
  }
);

const handleBaselineToggle = (checked: boolean, channel: Channel) => {
  channel.isCo2EmissionsBaseline = !checked;
};

const dirtyChannelField = (channel: Channel, field: keyof Channel) => {
  const initialChannel = props.initialChannels.find((c) => c.id === channel.id);
  if (!initialChannel) {
    return channel[field] !== '';
  }
  return initialChannel[field] !== channel[field];
};
</script>
