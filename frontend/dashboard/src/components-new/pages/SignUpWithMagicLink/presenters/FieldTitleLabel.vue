<template>
  <div class="flex flex-col justify-center bg-gray-100 h-full">
    <div class="flex justify-between mx-3">
      <label :for="props.for" class="block">{{ props.title }}</label>
      <RequiredBadge />
    </div>
  </div>
</template>

<script setup lang="ts">
import RequiredBadge from './RequiredBadge.vue';
const props = defineProps<{
  title: string;
  for: string;
  required?: boolean;
}>();
</script>
