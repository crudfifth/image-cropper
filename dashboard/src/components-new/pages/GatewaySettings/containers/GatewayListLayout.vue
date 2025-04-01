<template>
  <div class="flex flex-col bg-white shadow-lg rounded-md">
    <div class="grid grid-cols-12 gap-6 p-6">
      <div class="col-span-12">
        <div>
          <div class="flex justify-between items-center pb-4">
            <h2 class="text-2xl font-bold">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="17.082"
                height="18.536"
                viewBox="0 0 17.082 18.536"
                class="w-5 h-5 inline mr-3 mb-1"
              >
                <g id="list_ordered_line" transform="translate(-3.918 -2.734)">
                  <path
                    id="Path_50841"
                    data-name="Path 50841"
                    d="M5.436,16.72a1.466,1.466,0,0,1,1.22,2.275,1.466,1.466,0,0,1-1.22,2.275,1.433,1.433,0,0,1-1.427-.9.65.65,0,1,1,1.2-.508.179.179,0,0,0,.165.109c.109,0,.23-.03.23-.167,0-.1-.073-.143-.156-.154l-.051,0a.65.65,0,0,1-.1-1.293l.1-.007c.1,0,.207-.037.207-.158,0-.137-.12-.167-.23-.167a.179.179,0,0,0-.164.11.65.65,0,1,1-1.2-.509,1.433,1.433,0,0,1,1.427-.9ZM20,18a1,1,0,0,1,0,2H9a1,1,0,0,1,0-2ZM6.08,9.945a1.552,1.552,0,0,1,.43,2.442l-.554.593h.47a.65.65,0,1,1,0,1.3H4.573a.655.655,0,0,1-.655-.654.76.76,0,0,1,.177-.557L5.559,11.5a.253.253,0,0,0-.06-.392.183.183,0,0,0-.275.142l-.006.059a.65.65,0,0,1-.65.65.664.664,0,0,1-.65-.7A1.482,1.482,0,0,1,6.081,9.945ZM20,11a1,1,0,0,1,.117,1.993L20,13H9a1,1,0,0,1-.117-1.993L9,11ZM6.15,3.39V6.63a.65.65,0,0,1-1.3,0V4.522a.65.65,0,0,1-.46-1.183l.742-.495a.655.655,0,0,1,1.018.545ZM20,4a1,1,0,0,1,.117,1.993L20,6H9a1,1,0,0,1-.117-1.993L9,4Z"
                    fill="#005da8"
                  />
                </g>
              </svg>
              ゲートウェイ一覧
            </h2>
            <div class="flex gap-2">
              <DeleteButton
                :disabled="!isAnyCheckboxChecked"
                :on-click-async="onDeleteButtonClick"
              />
              <SubmitButton
                :disabled="!isAnyCheckboxChecked"
                :on-click-async="onSubmitButtonClick"
              />
            </div>
          </div>
          <div class="px-2 p-6 overflow-auto h-96">
            <GatewayListTableLayout
              ref="gatewayListTable"
              @update:checked-channels="handleCheckedChannelsUpdate"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import GatewayListTableLayout from './GatewayListTableLayout.vue';
import DeleteButton from '../presenters/DeleteButton.vue';
import SubmitButton from '../presenters/SubmitButton.vue';
import GraphAdapterService from '@/services/GraphAdapterService';
import { openConfirmModal } from '@/stores/ConfirmModalStore';
import { openAlertModal } from '@/stores/AlertModalStore';

const isAnyCheckboxChecked = ref(false);

function handleCheckedChannelsUpdate(isChecked: boolean) {
  isAnyCheckboxChecked.value = isChecked;
}

const gatewayListTable = ref<typeof GatewayListTableLayout | null>(null);

const onDeleteButtonClick = async () => {
  const selectedGatewayIds = gatewayListTable.value?.getSelectedGatewayIds();
  if (!selectedGatewayIds) { //エラーハンドリング
    openAlertModal({
      body: '選択されたゲートウェイがありません。',
    });
    return;
  }

  const isUsedInGraphResults = await Promise.all(
    selectedGatewayIds.map((id: string) => GraphAdapterService.isGatewayUsedInTrendGraph(id))
  );

  if (isUsedInGraphResults.includes(true)) {
    openAlertModal({
      body: 'トレンドグラフ表示に削除しようとしているゲートウェイが使われています。表示設定画面でゲートウェイ名を確認してください。',
    });
    return;
  }

  const confirmMessage =
    'ゲートウェイを削除しますと、データがクリアされます。' +
    '現在収集したデータを保存する場合は、トレンドグラフ画面よりCSVファイルのダウンロードを必要に応じて行ってください。';
  openConfirmModal({
    body: confirmMessage,
    onResponse: async (confirmed: boolean) => {
      if (confirmed && gatewayListTable.value) {
        await gatewayListTable.value.deleteAction();
      }
    },
  });
};

const onSubmitButtonClick = async () => {
  if (gatewayListTable.value) {
    await gatewayListTable.value.submitAction();
  }
};

const refreshListAction = async () => {
  if (gatewayListTable.value) {
    await gatewayListTable.value.refreshListAction();
  }
};

defineExpose({ refreshListAction });

</script>
