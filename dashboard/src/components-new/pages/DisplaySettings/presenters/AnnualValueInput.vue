<template>
  <div class="flex items-center mb-3">
    <div class="flex items-center w-2/5">
      <h3 class="text-sm mr-3">{{ itemName }}</h3>
    </div>
    <div class="relative w-3/5">
      <NonNegativeNumberInput 
        v-model.number="currentValue"
        class="text-left text-slate-700 bg-sky-50 p-2 rounded-md w-full pr-10"
        :class="{ 'border-3 border-green-200': dirty && currentValue >= 0 }"
        @blur="handleBlur"
      />
      <span class="absolute inset-y-0 right-2 flex items-center text-slate-700">
        {{ unit }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import NonNegativeNumberInput from '@inputs/NonNegativeNumberInput.vue'; 

const props = defineProps({
  modelValue: { type: Number, required: true },
  itemName: { type: String, required: true },
  unit: { type: String, required: true },
  dirty: { type: Boolean, default: false },
});

const emit = defineEmits(['update:modelValue']);

const currentValue = ref(props.modelValue);

const handleBlur = () => {
  emit('update:modelValue', currentValue.value);
};

watch(
  () => props.modelValue,
  (newValue) => {
    currentValue.value = newValue;
  }
);
</script>
