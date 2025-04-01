<template>
  <table class="text-base table-auto text-center border-b-2 min-w-full">
    <thead class="text-sm table-auto text-center border-b-2 min-w-full">
      <tr class="[&>th]:text-sm px-4 py-1 text-md">
        <th rowspan="2" class="w-20">
          <span class="ml-3 mr-3 whitespace-nowrap">チェック</span>
        </th>
        <th rowspan="2" class="w-48 py-1">
          <span class="whitespace-nowrap"> 種別 </span>
        </th>
        <th rowspan="2" class="w-64 py-1">
          <span class="whitespace-nowrap">ゲートウェイ名</span>
        </th>
        <th rowspan="2" class="w-48 py-1">
          <span class="whitespace-nowrap">ゲートウェイID</span>
        </th>
        <th rowspan="2" class="px-4 w-32 py-1">
          <span class="whitespace-nowrap">利用開始日</span>
        </th>
        <th rowspan="2" class="px-4 w-32 py-1">
          <span class="whitespace-nowrap">利用可能期限</span>
        </th>
        <th colspan="2" class="text-center border-b-2 w-32 py-1">
          <span class="whitespace-nowrap">ステータス</span>
        </th>
        <th rowspan="2" class="px-4 w-48 py-1">
          <span class="whitespace-nowrap">最終データ取得状況</span>
        </th>
        <th rowspan="2" class="px-4 w-32 py-1">
          <span class="whitespace-nowrap">ライセンス種別</span>
        </th>
      </tr>
      <tr class="text-center">
        <th class="w-16 py-1">電波</th>
        <th class="w-16 py-1">接続</th>
      </tr>
    </thead>
    <tbody class="divide-y">
      <tr
        v-for="(gateway, index) in gatewayListFields"
        :key="gateway.type"
        class="text-gray-700"
      >
        <td class="px-4 py-1 items-center">
          <input
            :id="'checkbox-' + gateway.type"
            v-model="checkedChannels[index]"
            type="checkbox"
            class="form-checkbox h-5 w-5 text-gray-600"
          />
        </td>
        <td class="py-1">{{ gateway.type }}</td>
        <td class="py-1">
          {{ gateway.name }}
        </td>
        <td class="py-1">
          {{ gateway.id }}
        </td>
        <td class="px-4 py-1">
          {{ gateway.startDate?.replace(/-/g, '/') ?? '-' }}
        </td>
        <td
          :class="{
            'text-red-500': isNextDayPast(gateway.licenseLimit),
          }"
          class="px-4 py-1"
        >
          {{ gateway.licenseLimit }}
        </td>
        <td>
          <div class="flex justify-center">
            <SignalLevelIcon :level="gateway.signalLevel" />
          </div>
        </td>
        <td>
          <div class="flex justify-center">
            <ConnectionStatusIcon
              :connection-status="gateway.connectionState"
              class="scale-150"
            />
          </div>
        </td>
        <td class="px-4 py-1">
          {{ format(new Date(gateway.updatedAt), 'yyyy/MM/dd HH:mm') }}
        </td>
        <td class="px-4 py-1">
          {{ gateway.licenseType }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { ref, onMounted, Ref, watch } from 'vue';
import { format } from 'date-fns';
import SignalLevelIcon from '@icons/SignalLevelIcon.vue';
import ConnectionStatusIcon from '@icons/ConnectionStatusIcon.vue';

import GatewayService from '@/services/GatewayService';
import GatewayStartDateService from '@/services/GatewayStartDateService';

type GatewayFieldType = {
  type: string;
  name: string;
  id: string;
  startDate: string | undefined;
  licenseLimit: string;
  signalLevel: number;
  connectionState: 'connected' | 'disconnected';
  updatedAt: string;
  licenseType: string;
};

const emit = defineEmits(['update:checkedChannels']);

const gatewayListFields: Ref<GatewayFieldType[]> = ref([]);

const checkedChannels = ref<boolean[]>(
  gatewayListFields.value.map(() => false)
);

watch(
  checkedChannels,
  () => {
    const isAnyChecked = checkedChannels.value.some(Boolean);
    emit('update:checkedChannels', isAnyChecked);
  },
  { deep: true }
);

const isNextDayPast = (dateString: string) => {
  const date = new Date(dateString);
  date.setDate(date.getDate() + 1);
  return date < new Date();
};

const getSelectedGatewayIds = () => {
  return gatewayListFields.value
    .filter((_, index) => checkedChannels.value[index])
    .map(gateway => gateway.id);
};

const refreshList = async () => {
  const gatewayListResponse = await GatewayService.fetchGatewayList();
  const gatewayStartDateResponses = await Promise.all(
    gatewayListResponse.map(async (res) => {
      return await GatewayStartDateService.fetchGatewayStartDate(res.id);
    })
  );
  gatewayListFields.value = gatewayListResponse.map((gateway) => {
    return {
      type: gateway.type,
      name: gateway.name,
      id: gateway.id,
      startDate: gatewayStartDateResponses.find(
        (res) => res?.gateway_id === gateway.id
      )?.started_at,
      licenseLimit: gateway.license_limit.replace(/-/g, '/'),
      signalLevel: gateway.signal_level,
      connectionState: gateway.connected ? 'connected' : 'disconnected',
      updatedAt: format(new Date(gateway.updated_at), 'yyyy/MM/dd HH:mm'),
      licenseType: gateway.license_type,
    };
  });
  checkedChannels.value = gatewayListFields.value.map(() => false);
};

// ライフサイクルメソッド
onMounted(async () => {
  await refreshList();
});

// 親コンポーネントに公開する関数
const refreshListAction = async () => {
  await refreshList();
};

const deleteAction = async () => {
  const toDelete = gatewayListFields.value.filter(
    (_, index) => checkedChannels.value[index]
  );

  await Promise.all(
    toDelete.map((gateway) => GatewayService.deleteGateway({ id: gateway.id }))
  );
  await refreshList();
};

const submitAction = async () => {
  // 今のところ編集可能なフィールドがないので、単に更新処理を行う
  await refreshList();
};


defineExpose({
  getSelectedGatewayIds,
  refreshListAction,
  deleteAction,
  submitAction,
});
</script>
