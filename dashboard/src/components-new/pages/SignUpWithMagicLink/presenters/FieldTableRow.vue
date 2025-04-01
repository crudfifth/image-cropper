<template>
  <div class="flex border-b">
    <div class="flex-1 min-w-72 max-w-72 h-16 p-0">
      <FieldTitleLabel
        :title="props.labelTitle"
        :for="props.id"
        :required="props.required"
      />
    </div>
    <div class="flex flex-col justify-center p-2">
      <div v-if="!fixed" class="flex items-center gap-2 mx-2">
        <PasswordInput
          v-if="props.password"
          :id="props.id"
          v-model="inputValue"
          class="w-72"
          :placeholder="props.placeholder"
          :required="props.required"
        />
        <input
          v-else
          :id="props.id"
          v-model="inputValue"
          class="form-input w-72"
          type="text"
          :placeholder="props.placeholder"
          :required="props.required"
        />
        <span
          v-if="props.caption && !props.error"
          class="mt-1 text-sm text-gray-500"
        >
          {{ props.caption }}
        </span>
        <span v-if="props.error" class="mt-1 text-sm text-red-500">
          {{ props.error }}
        </span>
      </div>
      <div v-else>
        <span class="mx-2">{{ inputValue }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import FieldTitleLabel from './FieldTitleLabel.vue';
import PasswordInput from '@inputs/PasswordInput.vue';
const props = defineProps<{
  labelTitle: string;
  id: string;
  placeholder?: string;
  fixed?: boolean;
  required?: boolean;
  password?: boolean;
  caption?: string;
  error?: string;
}>();

const inputValue = defineModel<string>({ default: '' });
</script>
