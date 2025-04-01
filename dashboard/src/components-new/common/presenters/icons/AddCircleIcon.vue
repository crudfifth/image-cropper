<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="20"
    height="20"
    viewBox="0 0 20 20"
  >
    <g id="add_circle_line" transform="translate(-2 -2)">
      <path
        id="Path_50863"
        data-name="Path 50863"
        d="M12,2A10,10,0,1,1,2,12,10,10,0,0,1,12,2Zm0,2a8,8,0,1,0,8,8A8,8,0,0,0,12,4Zm0,3a1,1,0,0,1,1,1v3h3a1,1,0,0,1,0,2H13v3a1,1,0,0,1-2,0V13H8a1,1,0,0,1,0-2h3V8A1,1,0,0,1,12,7Z"
        :fill="color"
      />
    </g>
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ color: string }>(), {
  color: 'white',
});
</script>
