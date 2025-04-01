<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="15.984"
    height="19.979"
    viewBox="0 0 15.984 19.979"
    fill="currentColor"
    :class="color"
  >
    <g transform="translate(-4.004 -2)">
      <path
        d="M8.084,2.6A1.01,1.01,0,0,1,9.007,2h7.977a1.01,1.01,0,0,1,.9,1.462L15.618,8h3.358a1.01,1.01,0,0,1,.714,1.724L7.737,21.677a1.01,1.01,0,0,1-1.672-1.034L8.613,13h-3.6a1.01,1.01,0,0,1-.923-1.42Z"
      />
    </g>
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ color: string }>(), {
  color: '',
});
</script>
