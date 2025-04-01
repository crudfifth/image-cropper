<template>
  <main class="bg-main-blue">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full md:w-1/2 m-auto">
        <div class="min-h-screen h-full flex flex-col justify-center">
          <div class="max-w-md mx-auto px-4 py-8 bg-white rounded">
            <h1 class="text-3xl text-slate-800 font-bold mb-6">
              IHI ダッシュボード
            </h1>
            <!-- Form -->
            <div>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium mb-1" for="email"
                    >メールアドレス</label
                  >
                  <input
                    id="email"
                    v-model="email"
                    class="form-input w-full"
                    type="email"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1" for="password"
                    >パスワード
                  </label>
                  <PasswordInput id="password" v-model="password" />
                </div>
                <div class="mt-2">
                  <input
                    id="rememberMe"
                    v-model="isRememberMe"
                    type="checkbox"
                  />
                  <label for="rememberMe" class="ml-2 text-xs"
                    >次回から入力を省略する
                  </label>
                </div>
              </div>
              <div class="text-red-700 text-sm whitespace-pre-wrap mt-2">
                {{ errorMessage }}
              </div>
              <div class="flex items-center justify-between mt-6">
                <div class="mr-1">
                  <router-link
                    class="text-sm underline hover:no-underline"
                    to="/request-reset-password"
                    >パスワードをお忘れの方</router-link
                  >
                </div>
                <button
                  class="btn bg-indigo-500 hover:bg-indigo-600 text-white ml-3"
                  @click="signIn"
                >
                  ログイン
                </button>
              </div>
            </div>
            <TermsOfServiceDialog
              title="ご利用規約"
              :modal-open="isModalOpen"
              :on-agree="agreeTermOfServiceFunction"
              @close-modal="isModalOpen = false"
            >
            </TermsOfServiceDialog>
            <!-- Footer -->
          </div>
          <div class="mt-5 text-center">
            <button
              class="btn bg-indigo-500 hover:bg-indigo-600 text-white ml-3"
              @click.stop="openTermsOfService"
            >
              ご利用規約
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { AxiosError } from 'axios';
import UserService from '@/services/UserService';
import TermsOfServiceDialog from '@/components/TermsOfServiceDialog.vue';
import PasswordInput from '@/components/ui-parts/PasswordInput.vue';

const router = useRouter();

const email = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);
const isRememberMe = ref(false);
const isModalOpen = ref(false);
const agreeTermOfServiceFunction = ref<(() => Promise<void>) | undefined>(
  undefined
);

const signIn = async () => {
  isLoading.value = true;

  const mEmail = email.value;
  const mPass = password.value;
  const mIsRememberMe = isRememberMe.value;

  try {
    await UserService.signIn({
      email: mEmail,
      password: mPass,
      isRememberMe: mIsRememberMe,
    });

    const user = await UserService.fetchCurrentUser();
    if (!user) {
      throw new Error('ユーザー情報の取得に失敗しました');
    }

    if (!user.is_agreed_to_terms_of_service) {
      openTermsOfServiceWithAgreeButton(user.id);
      return;
    }

    goToHome();
  } catch (catchedError) {
    const error = catchedError as AxiosError;
    isLoading.value = false;
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

const goToHome = () => {
  router.push('/');
};

const goToChangePassword = () => {
  router.push({ name: 'changePassword' });
};

const openTermsOfService = () => {
  agreeTermOfServiceFunction.value = undefined;
  isModalOpen.value = true;
};

const openTermsOfServiceWithAgreeButton = (userId: string) => {
  agreeTermOfServiceFunction.value = async () => {
    await openTermsOfServiceAgree(userId);
  };
  isModalOpen.value = true;
};

const openTermsOfServiceAgree = async (userId: string) => {
  await UserService.agreeToTermsOfService(userId);
  isModalOpen.value = false;
  goToChangePassword();
};
</script>
