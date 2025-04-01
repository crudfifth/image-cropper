<template>
  <div class="bg-main-bg w-full px-32 py-20 rounded-lg shadow-lg">
    <div class="flex flex-col justify-center gap-8">
      <div class="flex justify-center">
        <span class="text-xl font-bold">以下に情報を入力してください</span>
      </div>

      <div class="flex flex-col gap-4">
        <input
          v-model="email"
          type="email"
          class="form-input"
          placeholder="メールアドレス"
        />
      </div>
    </div>

    <div class="flex justify-center mt-8 gap-8">
      <router-link
        to="/signin"
        class="btn bg-gray-500 hover:bg-gray-400 text-white font-bold w-44"
      >
        <div class="flex items-center">
          <LeftArrowIcon class="w-4 h-4" color="text-white" />
          <span class="ml-4 font-bold text-base"> キャンセル </span>
        </div>
      </router-link>
      <AsyncFunctionButton
        :on-click-async="requestResetPassword"
        class="flex items-center justify-center px-4 rounded bg-blue-500 hover:bg-blue-600 text-white font-bold w-64"
        :disabled="!meta.valid"
      >
        <div class="flex items-center">
          <KeyIcon class="w-4 h-4" color="text-white" />
          <span class="ml-4 font-bold text-base"> パスワードを再設定する </span>
        </div>
      </AsyncFunctionButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import KeyIcon from '@icons/KeyIcon.vue';
import LeftArrowIcon from '@icons/LeftArrowIcon.vue';
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
import UserService from '@/services/UserService';
import { openAlertModal } from '@/stores/AlertModalStore';

import { useField } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { z } from 'zod';

const { value: email, meta } = useField(
  'email',
  toTypedSchema(z.string().email())
);

const requestResetPassword = async () => {
  try {
    await UserService.requestResetPassword(email.value);
  } catch (error) {
    openAlertModal({
      body: 'パスワード再設定時にエラーが発生しました。',
    });
    return;
  }

  openAlertModal({
    body: 'メール内のリンク先のページで、パスワードの再設定を完了してください。',
    title: 'パスワード再設定メールを送信しました',
  });
};
</script>
