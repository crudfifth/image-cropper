<template>
  <div class="col-span-3">
    <div
      class="mb-6 flex flex-col col-span-4 text-white bg-main-blue shadow-lg rounded-md h-full"
    >
      <div class="p-6">
        <h2 class="text-2xl mb-2">
          <UserIcon class="w-6 h-6 inline mr-3 mb-1" />
          <span class="font-bold">ユーザー設定</span>
        </h2>
        <div v-for="field in fields" :key="field.key" class="items-center mb-3">
          <div class="flex items-center font-bold">
            <h3 class="text-lg mr-3 mb-1">{{ field.name }}</h3>
          </div>
          <div class="relative">
            <div
              class="text-9xl font-light text-center mb-8 text-slate-700 bg-sky-50 p-2 rounded-md w-full"
            >
              {{ field.value ?? '-' }}
            </div>
            <span
              class="text-2xl font-light absolute bottom-4 right-4 flex items-end text-slate-700"
            >
              {{ field.unit }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watchEffect } from 'vue';
import UserCountService from '@/services/UserCountService';
import UserIcon from '@icons/UserIcon.vue';
import { userCountStore } from '@/stores/UserSettingsStore';

const screenWidth = ref(window.innerWidth);
const handleResize = () => {
  screenWidth.value = window.innerWidth;
};
onMounted(async () => {
  window.addEventListener('resize', handleResize);

  const userCounts = await UserCountService.fetchRegisteredUserCount();
  userCountStore.userLimit = userCounts.user_limit;
  userCountStore.userCount = userCounts.user_count;
  userCountStore.activeUserCount = userCounts.active_user_count;

  fields.value = [
    { ...fields.value[0], value: userCountStore.userLimit },
    { ...fields.value[1], value: userCountStore.userCount },
    { ...fields.value[2], value: userCountStore.activeUserCount },
  ];
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

const fields = ref([
  {
    key: 'userLimit',
    name: '登録上限数',
    unit: '人',
    value: undefined as number | undefined,
  },
  {
    key: 'userCount',
    name: '登録数',
    unit: '人',
    value: undefined as number | undefined,
  },
  {
    key: 'activeCount',
    name: 'アクティブ数',
    unit: '人',
    value: undefined as number | undefined,
  },
]);

watchEffect(() => {
  fields.value = [
    { ...fields.value[0], value: userCountStore.userLimit },
    { ...fields.value[1], value: userCountStore.userCount },
    { ...fields.value[2], value: userCountStore.activeUserCount },
  ];
});
</script>
