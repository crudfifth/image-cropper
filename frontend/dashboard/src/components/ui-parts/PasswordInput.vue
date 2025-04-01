<!-- 
  パスワード入力用inputのコンポーネント。
  パスワードの表示・非表示ボタンを内包している。
-->

<template>
  <div class="relative col-span-7 w-full">
    <input
      id="new_password"
      v-model="passwordText"
      class="col-span-7 form-input w-full"
      :type="isShowPassword ? 'text' : 'password'"
    />
    <label
      for="password2_sh"
      class="h-4 absolute my-auto inset-y-1/2 right-2 cursor-pointer peer"
    >
      <input
        id="password2_sh"
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
import PasswordVisibleIcon from '@/components/icons/password-input/PasswordVisibleIcon.vue';
import PasswordHiddenIcon from '@/components/icons/password-input/PasswordHiddenIcon.vue';
defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const passwordText = ref<string>('');
const isShowPassword = ref<boolean>(false);

watch(passwordText, (newVal) => {
  emit('update:modelValue', newVal);
});
</script>
