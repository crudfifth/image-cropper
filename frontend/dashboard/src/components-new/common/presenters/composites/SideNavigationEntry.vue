<template>
  <router-link
    v-slot="{ href, navigate, isExactActive }"
    :to="{ path: path, query: $route.query }"
    custom
  >
    <li
      v-if="isExpanded"
      class="px-3 py-2 rounded-md m-2"
      :class="
        isExactActive && 'bg-main-blue text-white border-r-4 border-pink-500'
      "
    >
      <a
        class="block truncate transition duration-150 hover:text-slate-400"
        :class="isExactActive ? 'hover:text-slate-900' : 'hover:text-slate-400'"
        :href="href"
        @click="navigate"
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
      </a>
    </li>
    <li v-else>
      <a
        class="block truncate transition duration-150 hover:text-slate-400 flex justify-center"
        :class="isExactActive ? 'hover:text-slate-900' : 'hover:text-slate-400'"
        :href="href"
        @click="navigate"
      >
        <component
          :is="iconComponent"
          :color="isExactActive ? 'text-white' : 'text-main-blue'"
          class="w-7 h-7 my-2 flex-shrink-0 p-1"
          :class="isExactActive && 'bg-main-blue text-white rounded-md '"
        ></component>
      </a>
    </li>
  </router-link>
</template>
<script setup lang="ts">
import { useRoute } from 'vue-router';
useRoute();

defineProps<{
  path: string;
  label: string;
  iconComponent: any; // eslint-disable-line
  isExpanded: boolean;
}>();
</script>
