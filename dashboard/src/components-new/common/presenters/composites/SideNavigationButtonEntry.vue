<template>
  <button @click="handler">
    <li
      v-if="isExpanded"
      class="px-3 py-2 rounded-md m-2"
      :class="
        isExactActive && 'bg-main-blue text-white border-r-4 border-pink-500'
      "
    >
      <div class="flex items-center">
        <component
          :is="iconComponent"
          :color="isExactActive ? 'text-white' : 'text-main-blue'"
          class="w-6 h-6 flex-shrink-0"
        ></component>
        <span
          class="text-sm font-medium ml-3 lg:opacity-0 lg:sidebar-expanded:opacity-100 2xl:opacity-100 duration-200"
        >
          {{ label }}
        </span>
      </div>
    </li>
    <li v-else>
      <component
        :is="iconComponent"
        :color="isExactActive ? 'text-white' : 'text-main-blue'"
        class="w-7 h-7 my-2 flex-shrink-0 p-1"
        :class="isExactActive && 'bg-main-blue text-white rounded-md '"
      ></component>
    </li>
  </button>
</template>
<script setup lang="ts">
defineProps<{
  label: string;
  handler: () => void;
  iconComponent: any; //eslint-disable-line
  isExpanded: boolean;
}>();

// 「現在のページがナビゲーション対象のページである」という状態。
// TODO: ナビゲーションを行わないボタンなので、isExactActive自体をあとで消す
const isExactActive = false;
</script>
