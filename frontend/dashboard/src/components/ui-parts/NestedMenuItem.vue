<template>
  <li
    class="relative min-w-64"
    @mouseover="handleMouseOver"
    @mouseleave="handleMouseLeave"
  >
    <div
      class="cursor-pointer hover:bg-main-blue hover:text-white p-2"
      @click="handleClick"
    >
      {{ props.menuItem.name }}
    </div>
    <ul
      v-show="isSubMenuVisible"
      class="absolute left-full top-0 bg-white border border-gray-200 shadow-md"
      :style="{ width: 'max-content' }"
    >
      <NestedMenuItem
        v-for="subItem in props.menuItem.subMenu"
        :key="subItem.id"
        :menu-item="subItem"
        :on-click="onClick"
        :style="{ width: 'max-content' }"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import { ref } from 'vue';

export type MenuItem = {
  id: string;
  name: string;
  subMenu?: MenuItem[];
};

const props = defineProps<{
  menuItem: MenuItem;
  onClick: (menuItem: MenuItem, event: Event) => void;
}>();

const isSubMenuVisible = ref(false);

const handleMouseOver = () => {
  isSubMenuVisible.value = true;
};

const handleMouseLeave = () => {
  isSubMenuVisible.value = false;
};

const handleClick = (event: Event) => {
  props.onClick(props.menuItem, event);
};
</script>
