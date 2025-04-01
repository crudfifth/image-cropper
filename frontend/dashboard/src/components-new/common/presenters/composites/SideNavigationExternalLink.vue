<template>
  <li v-if="isExpanded" class="px-3 py-2 rounded-md m-2">
    <a
      class="block truncate transition duration-150 hover:text-slate-400"
      :href="url"
      target="_blank"
    >
      <div class="flex items-center">
        <component
          :is="iconComponent"
          class="w-6 h-6 flex-shrink-0"
        ></component>
        <span
          class="text-sm font-medium ml-3 lg:opacity-0 lg:sidebar-expanded:opacity-100 2xl:opacity-100 duration-200"
        >
          {{ label }}
        </span>
      </div>
    </a>
  </li>
  <li v-else>
    <a
      class="block truncate transition duration-150 hover:text-slate-400 flex justify-center"
      :href="url"
      target="_blank"
    >
      <component
        :is="iconComponent"
        class="w-7 h-7 my-2 flex-shrink-0 p-1"
      ></component>
    </a>
  </li>
</template>
<script setup lang="ts">
import { useRoute } from 'vue-router';
useRoute();

defineProps<{
  url: string;
  label: string;
  iconComponent: any; // eslint-disable-line
  isExpanded: boolean;
}>();
</script>
