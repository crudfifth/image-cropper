<!-- 負ではない(つまり0以上の)値だけを入力できる数値input -->
<template>
  <input
    :value="localValue"
    @input="updateValue($event)"
    type="number"
    :min="minValue"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: Number,
  minValue: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits<{
  (event: 'update:modelValue', value: number): void
}>();

const localValue = ref(props.modelValue);

watch(() => props.modelValue, (newVal) => {
  if (newVal != null && newVal < props.minValue) {
    localValue.value = props.minValue;
  } else {
    localValue.value = newVal;
  }
});

function updateValue(event: Event) {
  const target = (event.target as HTMLInputElement | null);
  if (!target) return;
  const newValue = target.value.trim();
  if (newValue === '') {
    localValue.value = props.minValue;
    emit('update:modelValue', props.minValue);
    return;
  }
  let numericValue = Number(newValue);
  if (isNaN(numericValue)) {
    localValue.value = props.minValue;
    emit('update:modelValue', props.minValue);
  } else {
    const validatedValue = Math.max(numericValue, props.minValue);
    localValue.value = validatedValue;
    emit('update:modelValue', validatedValue);
  }
}

</script>
