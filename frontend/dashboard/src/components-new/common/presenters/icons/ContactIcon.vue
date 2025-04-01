<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18" height="13.5"
    viewBox="0 0 18 13.5"
  >
    <path 
      d="M0-3.375a2.687,2.687,0,0,1-1.658-.577L-9-9.661v7.973A1.688,1.688,0,0,0-7.312,0H7.313A1.687,1.687,0,0,0,9-1.687V-9.661L1.659-3.948A2.708,2.708,0,0,1,0-3.375Zm-8.427-7.267,7.46,5.8a1.576,1.576,0,0,0,1.936,0l7.46-5.8A1.588,1.588,0,0,0,9-11.812,1.688,1.688,0,0,0,7.313-13.5H-7.312A1.687,1.687,0,0,0-9-11.812a1.484,1.484,0,0,0,.573,1.171Z"
      transform="translate(9 13.5)"
      fill="#005da8"
    />
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ color: string }>(), {
  color: 'text-main-blue',
});
</script>
