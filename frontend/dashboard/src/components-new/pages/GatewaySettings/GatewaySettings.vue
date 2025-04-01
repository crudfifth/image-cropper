<template>
  <PageLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-10xl mx-auto">
      <div class="grid grid-cols-12 gap-6">
        <GatewaySettingsLayout />
        <div class="col-span-9 flex flex-col">
          <AddGatewayLayout :request-refresh-list="refreshListAction" />
          <GatewayListLayout ref="gatewayListLayout" />
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PageLayout from '@components/common/containers/PageLayout.vue';
import AddGatewayLayout from './containers/AddGatewayLayout.vue';
import GatewayListLayout from './containers/GatewayListLayout.vue';
import GatewaySettingsLayout from './containers/GatewaySettingsLayout.vue';

// 子コンポーネントのインスタンス
const gatewayListLayout = ref<typeof GatewayListLayout | null>(null);

const refreshListAction = async () => {
  if (gatewayListLayout.value) {
    await gatewayListLayout.value.refreshListAction();
  }
};

</script>