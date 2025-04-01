<template>
  <PageLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8 w-full mx-auto">
      <div class="flex gap-6 w-full">
        <!-- 左セクション -->
        <div class="class=max-w-100 min-w-100">
          <div class="mb-6">
            <!-- 年間目標値 -->
            <YearlyTargetValue />
          </div>
          <div>
            <!-- 原単位設定詳細 -->
            <YearlyProductTable />
          </div>
        </div>

        <!-- <div class="w-full bg-red-500 flex-grow"></div> -->
        <div class="flex flex-col w-full overflow-x-auto">
          <SettingChannel
            v-model="selectedChannelIds"
            :co2-emissions-factors="co2EmissionsFactors"
            :channels="channelDataList"
            :initial-channels="initialChannelDataList"
            :gateways="gateways ?? []"
            @save-channels="saveChannels"
            @cancel="cancelChannelUpdate"
            @delete="deleteChannels"
            @change-channel-check="onChangeChannelCheck"
          />
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import PageLayout from '@components/common/containers/PageLayout.vue';
import ActionButton from './presenters/ActionButton.vue';
import SettingChannel, { Channel } from './containers/SettingChannelTable.vue';
import YearlyProductTable from './containers/YearlyProductTable.vue';
import YearlyTargetValue from './containers/YearlyTargetValue.vue';

import { GraphAdapterGateway } from '@/repositories/GraphAdapterRepository';
import GraphAdapterService from '@/services/GraphAdapterService';
import Co2EmissionsFactorsService from '@/services/Co2EmissionsFactorsService';

import { onMounted, ref } from 'vue';
import { isEqual } from 'lodash-es';
import { openConfirmModal } from '@/stores/ConfirmModalStore';
import { openAlertModal } from '@/stores/AlertModalStore';
import { Co2EmissionsFactors } from '@/repositories/Co2EmissionsFactorsRepository';

const channelDataList = ref<Channel[]>([]);
const initialChannelDataList = ref<Channel[]>([]);
const gateways = ref<GraphAdapterGateway[] | undefined>(undefined);
const co2EmissionsFactors = ref<Co2EmissionsFactors>([]);
const selectedChannelIds = ref<number[]>([]);

onMounted(async () => {
  const channels = await GraphAdapterService.fetchChannelDataList();
  channelDataList.value = channels.map(x => {
    return {
      ...x,
      formula: x.formula || '(x)',
    }
  });
  
  initialChannelDataList.value = JSON.parse(
    JSON.stringify(channelDataList.value)
  );
  gateways.value = await GraphAdapterService.fetchGraphAdapterGateways();
  co2EmissionsFactors.value =
    await Co2EmissionsFactorsService.fetchCo2EmissionsFactorValues();
});

const saveChannels = async (channels: Channel[]) => {
  if (isEqual(channels, initialChannelDataList.value)) {
    return;
  }
  const data = channels.map((channel) => ({
    graph_name: channel.name,
    graph_no: channel.id,
    co2_emissions_baseline: channel.baseline,
    co2_emissions_improvement_rate: channel.improvementRate,
    co2_emissions_current: channel.currentdata,
    device_no: channel.selectedChannel,
    equation_str: channel.formula,
    gateway_id: channel.selectedGateway,
    utility_cost_price: channel.unitPrice,
    is_co2_emissions_baseline: channel.isCo2EmissionsBaseline,
  }));
  try {
    await GraphAdapterService.updateGraphAdapters(data);
    openAlertModal({
      body: 'データを保存しました',
    });
    initialChannelDataList.value = JSON.parse(
      JSON.stringify(channelDataList.value)
    );
  } catch (e) {
    openAlertModal({
      body: 'データの保存に失敗しました',
    });
    return;
  }
};

const cancelChannelUpdate = () => {
  openConfirmModal({
    body: '編集中のデータを破棄しますか？',
    onResponse: (confirmed: boolean) => {
      if (confirmed) {
        channelDataList.value = JSON.parse(
          JSON.stringify(initialChannelDataList.value)
        );
      }
    },
  });
};

const deleteChannels = async () => {

  try {
    await GraphAdapterService.deleteGraphAdapterList(selectedChannelIds.value);
    channelDataList.value = channelDataList.value.map((channel) => {
      if (selectedChannelIds.value.includes(channel.id)) {
        return {
          ...channel,
          name: '',
          currentdata: 0,
          selectedGateway: null,
          selectedChannel: 0,
          formula: '(x)',
          unitPrice: 0,
          baseline: 0,
          improvementRate: 0,
        };
      }
      return channel;
    });
    openAlertModal({
      body: 'データを削除しました',
    });
    initialChannelDataList.value = JSON.parse(
      JSON.stringify(channelDataList.value)
    );
  } catch (e) {
    openAlertModal({
      body: 'データの削除に失敗しました',
    });
    return;
  }
};

const onChangeChannelCheck = (channelIds: number[]) => {
  selectedChannelIds.value = [...channelIds];
};
</script>
