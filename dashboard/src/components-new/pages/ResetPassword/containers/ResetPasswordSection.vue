<template>
  <div class="bg-main-bg w-full px-32 py-20 rounded-lg shadow-lg">
    <form>
      <div class="flex flex-col justify-center gap-4">
        <div class="flex flex-col items-center justify-center gap-4 m-4">
          <span class="text-xl font-bold">パスワード再設定</span>
          <div>
            <p class="text-sm">パスワードは、以下の規則に従ってください。</p>
            <ul class="list-disc pl-5 text-sm">
              <li>12文字以上かつ16文字以下</li>
              <li>
                半角の英字(大文字)、英字(小文字)、数字、記号それぞれすべてを最低1文字以上含む
              </li>
              <li>
                入力可能な記号のリスト:
                <code class="bg-blue-100 text-blue-500 p-1 text-sm rounded">
                  @ # $ % ^ &amp; * - _ + = [ ] { } | \ : ' , ? / ` ~ " ( ) ;
                </code>
              </li>
            </ul>
          </div>
        </div>

        <div class="flex flex-col items-center gap-4">
          <PasswordInput
            id="password"
            v-model="password"
            placeholder="新しいパスワード"
            class="w-80"
          />
          <PasswordInput
            id="password"
            v-model="confirm"
            placeholder="新しいパスワードの確認"
            class="w-80"
          />
        </div>
        <div class="flex justify-center">
          <div>
            <p class="text-red-500">
              {{
                debouncedErrors['password.password']
                  ? debouncedErrors['password.password']
                  : debouncedErrors.password
              }}&nbsp;
            </p>
          </div>
        </div>
      </div>

      <div class="flex justify-center mt-8 gap-8 h-10">
        <AsyncFunctionButton
          :on-click-async="resetPassword"
          :class="[
            'flex items-center justify-center px-4 rounded text-white font-bold w-64',
            !meta.valid ? 'bg-gray-500' : 'bg-blue-500 hover:bg-blue-600',
          ]"
          :disabled="!meta.valid"
        >
          <div class="flex items-center">
            <KeyIcon class="w-4 h-4" color="text-white" />
            <span class="ml-4 font-bold text-base">
              パスワードを再設定する
            </span>
          </div>
        </AsyncFunctionButton>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import PasswordInput from '@inputs/PasswordInput.vue';
import KeyIcon from '@icons/KeyIcon.vue';
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
import { openAlertModal } from '@/stores/AlertModalStore';
import { useRoute, useRouter } from 'vue-router';
import { ref, watch } from 'vue';
import { passwordSchema } from '@/zod-schemas/PasswordSchema';
import { useField, useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { z } from 'zod';
import { debounce } from 'lodash-es';
import UserService from '@/services/UserService';
import {
  InvalidPasswordError,
  InvalidTokenError,
} from '@/services/UserService';

const route = useRoute();
const router = useRouter();

const validationSchema = toTypedSchema(
  z.object({
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

const { value: password } = useField<string>('password.password');
const { value: confirm } = useField<string>('password.confirm');

const resetPassword = async () => {
  const token = route.query.token;
  if (typeof token !== 'string') {
    return;
  }

  try {
    await UserService.resetPassword({ token, password: password.value });
    openAlertModal({
      body: 'パスワードを変更しました。',
    });
    router.push('/');
  } catch (error) {
    if (error instanceof InvalidTokenError) {
      openAlertModal({
        body: 'パスワード再設定リンクが正しくありません。再度パスワード設定をお願いします。',
      });
      router.push('/');
      return;
    }

    if (error instanceof InvalidPasswordError) {
      openAlertModal({
        body: 'パスワードが正しくありません。',
      });
      router.push('/');
      return;
    }

    openAlertModal({
      body: '予期せぬエラーが発生しました。',
    });
  }
};
</script>
