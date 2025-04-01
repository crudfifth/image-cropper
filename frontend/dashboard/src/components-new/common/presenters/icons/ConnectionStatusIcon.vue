<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="28"
    height="40"
    viewBox="0 0 28 40"
  >
    <text
      id="_"
      data-name="●"
      transform="translate(14 31)"
      :fill="color"
      font-size="27"
      font-family="NotoSansJP-Medium, Noto Sans JP"
      font-weight="500"
    >
      <tspan x="-13" y="0">●</tspan>
    </text>
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ConnectionStatusType } from '@/types';
const props = withDefaults(
  defineProps<{ connectionStatus: ConnectionStatusType }>(),
  {
    connectionStatus: 'disconnected',
  }
);

const color = computed(() =>
  props.connectionStatus === 'connected' ? '#4caf50' : '#fb8c27'
);
</script>
