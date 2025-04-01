<template>
  <div
    class="justify-self-end flex justify-between gap-2 border bg-gray-50 rounded px-2 py-1"
  >
    <label v-for="option in options" :key="option" class="cursor-pointer">
      <input
        :checked="modelValue === option"
        type="radio"
        name="radioType"
        class="peer sr-only"
        :value="option"
        @change="$emit('update:modelValue', option)"
      />
      <div
        class="text-zinc-300 peer-checked:text-main-blue peer-checked:bg-white drop-shadow-md rounded px-2 py-1"
        aria-hidden="true"
      >
        {{ option }}
      </div>
    </label>
  </div>
</template>
<script setup lang="ts">
import { PropType } from 'vue';

defineProps({
  options: {
    type: Array as PropType<string[]>,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
});

defineEmits(['update:modelValue']);
</script>
