<!-- 
  パスワード入力用inputのコンポーネント。
  パスワードの表示・非表示ボタンを内包している。
-->

<template>
  <div class="relative">
    <input
      :id="'new_password' + randomId"
      v-model="passwordText"
      class="form-input w-full"
      :type="isShowPassword ? 'text' : 'password'"
      :placeholder="placeholder"
    />
    <label
      :for="'password2_sh' + randomId"
      class="h-4 absolute my-auto inset-y-1/2 right-2 cursor-pointer peer"
    >
      <input
        :id="'password2_sh' + randomId"
        v-model="isShowPassword"
        class="hidden peer"
        type="checkbox"
      />
      <PasswordHiddenIcon svg-class="peer-checked:hidden" />
      <PasswordVisibleIcon svg-class="hidden peer-checked:block" />
    </label>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import PasswordVisibleIcon from '../icons/PasswordVisibleIcon.vue';
import PasswordHiddenIcon from '../icons/PasswordHiddenIcon.vue';

const isShowPassword = ref<boolean>(false);

const props = defineProps<{
  modelValue: string;
  placeholder?: string;
}>();

const passwordText = ref(props.modelValue);

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void;
}>();

watch(
  () => props.modelValue,
  (newValue) => {
    passwordText.value = newValue;
  }
);

watch(passwordText, (newValue) => {
  emit('update:modelValue', newValue);
});

const randomId = crypto.randomUUID();
</script>
