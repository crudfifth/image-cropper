<template>
  <form>
    <div class="bg-main-bg w-full px-32 py-14 rounded-lg shadow-lg">
      <div class="flex flex-col justify-center gap-4">
        <div class="flex flex-col gap-4">
          <span class="font-bold">メールアドレス</span>
          <input v-model="email" type="email" class="form-input" />
        </div>
        <div class="flex flex-col gap-4">
          <span class="font-bold">パスワード</span>
          <PasswordInput v-model="password" />
        </div>
      </div>
      <div class="flex justify-center items-center mt-6">
        <span class="text-red-500">{{ errorMessage }} &nbsp;</span>
      </div>
      <div class="flex justify-center items-center mt-4">
        <input
          id="rememberMe"
          v-model="isRememberMe"
          type="checkbox"
          class="form-checkbox mr-4"
        />
        <label for="rememberMe" class="font-medium">
          次回から入力を省略する
        </label>
      </div>
      <div class="flex justify-center mt-8">
        <AsyncFunctionButton
          :on-click-async="signIn"
          :disabled="!(email && password)"
          :class="[
            'btn text-white font-bold w-64',
            !(email && password)
              ? 'bg-gray-400 hover:bg-gray-400'
              : 'bg-main-blue hover:bg-blue-900',
          ]"
        >
          <div class="flex items-center">
            <RightArrowIcon />
            <span class="ml-4 font-bold text-base"> ログイン </span>
          </div>
        </AsyncFunctionButton>
      </div>
      <div class="flex justify-center gap-6 mt-8">
        <div>
          <router-link
            class="text-sm underline hover:no-underline text-[#036db7]"
            to="/request-reset-password"
          >
            パスワードをお忘れの方
          </router-link>
        </div>
        <div>
          <button
            class="text-sm underline hover:no-underline text-[#036db7]"
            type="button"
            @click="showTermsOfServiceModal"
          >
            ご利用規約
          </button>
        </div>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import PasswordInput from '@inputs/PasswordInput.vue';
import AsyncFunctionButton from '@buttons/AsyncFunctionButton.vue';
import RightArrowIcon from '@icons/RightArrowIcon.vue';
import { openTermsModal } from '@/stores/TermsOfServiceModalStore';
import UserService from '@/services/UserService';
import { AxiosError } from 'axios';

const email = ref('');
const password = ref('');
const isRememberMe = ref(false);
const errorMessage = ref('');

const router = useRouter();

const signIn = async () => {
  try {
    await UserService.signIn({
      email: email.value,
      password: password.value,
      isRememberMe: isRememberMe.value,
    });

    router.push('/');
  } catch (catchedError) {
    const error = catchedError as AxiosError;
    if (error.response?.status === 401) {
      errorMessage.value =
        'ログインに失敗しました。\nIDまたはパスワードが間違っています。';
    } else if (error.response?.status === 403) {
      errorMessage.value =
        'ログインに失敗しました。\nアカウントがロックされています。';
    } else {
      console.error(error); // eslint-disable-line no-console
      errorMessage.value =
        'ログインに失敗しました。\n予期せぬエラーが発生しました。';
    }
    return;
  }
};

const showTermsOfServiceModal = () => {
  openTermsModal({ body: '利用規約' });
};
</script>
