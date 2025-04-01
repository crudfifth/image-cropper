<!-- 数式入力用のinput -->
<template>
  <div>
    <input
      v-model="value"
      class="form-input"
      name="formula"
      :class="{
        'border-2 border-red-500': errorMessage !== undefined,
        'border-2 border-blue-200': dirty && errorMessage === undefined,
      }"
    />
    <span class="text-sm text-red-500">{{ errorMessage }}</span>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useField } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { mathExpressionSchema } from '@/zod-schemas/MathExpressionSchema';
import { preprocessMathExpression } from '@/utils/PreprocessMathExpression';

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  dirty: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue', 'update:error']);

const { value, errorMessage } = useField(
  'formula',
  toTypedSchema(mathExpressionSchema)
);

onMounted(() => {
  value.value = props.modelValue;
});

watch(
  () => props.modelValue,
  (newValue) => {
    value.value = preprocessMathExpression(newValue);
    emit('update:modelValue', preprocessMathExpression(newValue));
  }
);

watch(value, (newValue) => {
  value.value = preprocessMathExpression(newValue);
  emit('update:modelValue', preprocessMathExpression(newValue));
});

watch(errorMessage, (newValue) => {
  emit('update:error', newValue !== undefined);
});
</script>
