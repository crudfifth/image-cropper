<!-- 「設定」画面のサイドバーをグルーピングするためのコンポーネント。現在は使われていない。 -->
<template>
  <li
    class="px-3 py-2 rounded-sm mb-0.5 last:mb-0"
    :class="activeCondition && 'bg-slate-900'"
  >
    <slot :handle-click="handleClick" :expanded="expanded"></slot>
  </li>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps({
  activeCondition: Boolean,
});

const expanded = ref(props.activeCondition);

const handleClick = () => {
  expanded.value = !expanded.value;
};
</script>
