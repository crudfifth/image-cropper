<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="19.999"
    viewBox="0 0 18 19.999"
    fill="currentColor"
    :class="color"
  >
    <g id="user_1_line" transform="translate(-3 -1)">
      <path
        id="Path_16455"
        data-name="Path 16455"
        d="M16,14a5,5,0,0,1,4.995,4.783L21,19v2a1,1,0,0,1-1.993.117L19,21V19a3,3,0,0,0-2.824-3L16,16H8a3,3,0,0,0-3,2.824L5,19v2a1,1,0,0,1-1.993.117L3,21V19a5,5,0,0,1,4.783-4.995L8,14ZM12,2A5,5,0,1,1,7,7a5,5,0,0,1,5-5Zm0,2a3,3,0,1,0,3,3,3,3,0,0,0-3-3Z"
        transform="translate(0 -1)"
      />
    </g>
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ color: string }>(), {
  color: '',
});
</script>
