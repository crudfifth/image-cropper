<template>
  <div class="flex flex-col bg-white shadow-lg rounded-md mb-4">
    <div class="grid grid-cols-12 gap-6 p-6">
      <div class="col-span-12">
        <div>
          <h2 class="text-2xl font-bold flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 20 20"
              class="w-5 h-5 inline mr-3 mb-1"
            >
              <g id="add_circle_line" transform="translate(-2 -2)">
                <path
                  id="Path_50839"
                  data-name="Path 50839"
                  d="M12,2A10,10,0,1,1,2,12,10,10,0,0,1,12,2Zm0,2a8,8,0,1,0,8,8A8,8,0,0,0,12,4Zm0,3a1,1,0,0,1,1,1v3h3a1,1,0,0,1,0,2H13v3a1,1,0,0,1-2,0V13H8a1,1,0,0,1,0-2h3V8A1,1,0,0,1,12,7Z"
                  fill="#005da8"
                />
              </g>
            </svg>
            ゲートウェイ追加
          </h2>
          <p class="text-black-600 font-bold text-s px-4 py-2">
            電源をオンにして電波に問題がないことを確認し、本体に記載されているIDを入力して登録をしてください。
          </p>

          <div class="flex justify-around items-start">
            <div class="flex-grow pr-7 pt-6">
              <img
                src="/src/images/IHI_Pushlog.png"
                class="w-full md:w-96 min-w-[200px]"
                alt="Pushlogパッケージ"
              />
            </div>

            <div class="flex-grow mt-9">
              <div class="flex flex-col">
                <div class="flex items-center py-1">
                  <div class="text-left px-4 font-bold w-40">
                    ゲートウェイ種類
                  </div>
                  <input
                    v-model="gatewayType"
                    type="text"
                    class="form-input rounded-md"
                    disabled
                  />
                </div>
                <div class="flex items-center py-1">
                  <div class="text-left px-4 font-bold w-40">
                    ゲートウェイ名
                  </div>
                  <input
                    v-model="gatewayName"
                    type="text"
                    class="form-input rounded-md"
                    placeholder="ゲートウェイの任意名称"
                  />
                </div>
                <div class="flex items-center py-1">
                  <div class="text-left px-4 font-bold w-40">
                    ゲートウェイID
                  </div>
                  <input
                    v-model="gatewayId"
                    type="text"
                    class="form-input rounded-md"
                    placeholder="123443211234123"
                  />
                  <AddButton
                    :on-click-async="onAddButonClick"
                    :disabled="
                      registeredGatewayCount.gateway_count >=
                      registeredGatewayCount.gateway_limit
                    "
                  />
                </div>
                <p class="text-red-600 font-bold text-s px-4 py-2">
                  {{ errorMessage }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AddButton from '../presenters/AddButton.vue';
import GatewayService from '@/services/GatewayService';
import type { RegisteredGatewayCountType } from '@/repositories/GatewayResistrationRepository';

const props = defineProps<{
  requestRefreshList: () => Promise<void>;
}>();

const errorMessage = ref<string>('');

const gatewayType = ref<string>('PUSHLOG'); // 今のところは"PUSHLOG"で固定。編集不可
const gatewayName = ref<string>('');
const gatewayId = ref<string>('');
const registeredGatewayCount = ref<RegisteredGatewayCountType>({
  gateway_limit: 0,
  gateway_count: 0,
  operations_count: 0,
});

const onAddButonClick = async () => {
  if (!gatewayName.value) {
    errorMessage.value = 'ゲートウェイ名を入力してください。';
    return;
  }

  if (!/^\d{15}$/.test(gatewayId.value)) {
    errorMessage.value =
      'ゲートウェイIDには、15桁の数値（ハイフンなし）を入力してください。';
    return;
  }

  const response = await GatewayService.createGateway({
    id: gatewayId.value,
    name: gatewayName.value,
  });

  if ('error' in response) {
    if (response.error.code === 'ERR_BAD_REQUEST') {
      const data = response.error.response?.data as string | undefined;
      if (
        data &&
        data.includes(
          'GatewayMaster with the provided gateway_id does not exist'
        )
      ) {
        errorMessage.value =
          'ゲートウェイIDを確認の上、IHIダッシュボード事務局までお問い合わせください。';
      } else {
        errorMessage.value = 'ゲートウェイ名が正しくありません。';
      }
    } else {
      errorMessage.value = '不明なエラーが発生しました。';
    }
  }
  await props.requestRefreshList();
};

onMounted(async () => {
  registeredGatewayCount.value =
    await GatewayService.fetchRegisterdGatewayCount();
});
</script>
