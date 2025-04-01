<template>
  <div class="flex flex-col gap-4">
    <h1 class="text-2xl font-bold">ユーザー情報</h1>
    <div class="flex flex-col">
      <div class="flex border-b" />
      <FieldTableRow
        id="user-name"
        v-model="userName"
        label-title="ユーザー名"
        placeholder="ユーザー名を入力"
        caption="例) 田中一郎"
        :error="debouncedErrors.userName"
        required
      />
      <FieldTableRow
        id="affiliation"
        v-model="affiliation"
        label-title="ユーザー部署名"
        placeholder="ユーザー部署名を入力"
        caption="例) 営業部"
        :error="debouncedErrors.affiliation"
        required
      />
      <FieldTableRow
        id="mail-address"
        v-model="mailAddress"
        label-title="メールアドレス(ログインID)"
        fixed
      />
      <FieldTableRow
        id="password"
        v-model="password"
        label-title="ログインパスワード"
        placeholder="パスワードを入力"
        caption="パスワードを入力してください"
        :error="
          debouncedErrors['password.password'] ?? debouncedErrors.password
        "
        password
        required
      />
      <FieldTableRow
        id="password-confirm"
        v-model="confirm"
        label-title="パスワード再入力"
        placeholder="パスワードを再入力"
        caption="確認のためもう一度入力してください"
        password
        required
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import FieldTableRow from '../presenters/FieldTableRow.vue';
import { watch, ref } from 'vue';
import { useForm, useField } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { passwordSchema } from '@/zod-schemas/PasswordSchema';
import { z } from 'zod';
import { debounce } from 'lodash-es';

export type UserFormInputValuesType = {
  userName: string;
  affiliation: string;
  mailAddress: string;
  password: string;
};

const validationSchema = toTypedSchema(
  z.object({
    userName: z.string().min(1, 'ユーザー名を入力してください。'),
    affiliation: z.string().min(1, 'ユーザー部署名を入力してください。'),
    mailAddress: z.string().optional(),
    password: z
      .object({
        password: passwordSchema.min(1, 'パスワードを入力してください。'),
        confirm: passwordSchema.min(1, 'パスワードを入力してください。'),
      })
      .refine(
        ({ password, confirm }) => password === confirm,
        'パスワードが同じではありません。'
      ),
  })
);

const { errors, meta } = useForm({
  validationSchema,
});

// 遅延バリデーション用のエラーメッセージ
const debouncedErrors = ref<typeof errors.value>({});
watch(
  errors,
  debounce((newErrors) => {
    debouncedErrors.value = newErrors;
  }, 1000),
  { deep: true }
);

const { value: userName } = useField<string>('userName');
const { value: affiliation } = useField<string>('affiliation');
const { value: mailAddress } = useField<string>('mailAddress');
const { value: password } = useField<string>('password.password');
const { value: confirm } = useField<string>('password.confirm');

const isValid = defineModel<boolean>('isValid', {
  default: false,
});

watch(
  () => meta.value,
  () => {
    isValid.value = meta.value.valid;
  }
);

const setUserInputs = (newVal: Partial<UserFormInputValuesType>) => {
  if (newVal.userName) {
    userName.value = newVal.userName;
  }
  if (newVal.affiliation) {
    affiliation.value = newVal.affiliation;
  }
  if (newVal.mailAddress) {
    mailAddress.value = newVal.mailAddress;
  }
  if (newVal.password) {
    password.value = newVal.password;
    confirm.value = newVal.password;
  }
};

const getUserInputs = () => {
  if (isValid.value) {
    return {
      userName: userName.value,
      affiliation: affiliation.value,
      mailAddress: mailAddress.value,
      password: password.value,
    };
  }
  return undefined;
};

defineExpose({
  setUserInputs,
  getUserInputs,
});
</script>
