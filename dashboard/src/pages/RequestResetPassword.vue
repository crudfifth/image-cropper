<template>
  <ModalLayout>
    <main class="bg-main-blue">
      <div class="relative flex">
        <!-- Content -->
        <div class="w-full">
          <div class="min-h-screen h-full flex flex-col justify-center">
            <div
              v-if="!isMailSent"
              class="max-w-md mx-auto px-4 py-8 bg-white rounded"
            >
              <h1 class="text-3xl text-slate-800 font-bold mb-6">
                パスワード再設定
              </h1>
              <!-- Form -->
              <form>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="email"
                      >メールアドレス<span class="text-rose-500">*</span></label
                    >
                    <input
                      id="email"
                      v-model="email"
                      class="form-input w-full"
                      type="email"
                    />
                  </div>
                </div>
                <div class="flex justify-between items-center mt-6">
                  <router-link
                    class="text-sm underline hover:no-underline"
                    to="/"
                    >戻る</router-link
                  >
                  <button
                    class="btn bg-indigo-500 hover:bg-indigo-600 text-white whitespace-nowrap"
                    @click.prevent="requestResetPassword"
                  >
                    パスワード再設定する
                  </button>
                </div>
              </form>
            </div>
            <div
              v-else
              class="text-center max-w-md mx-auto px-4 py-8 bg-white rounded"
            >
              <svg
                class="inline-flex w-16 h-16 fill-current mb-6"
                viewBox="0 0 64 64"
              >
                <circle class="text-emerald-100" cx="32" cy="32" r="32" />
                <path
                  class="text-emerald-500"
                  d="m28.5 41-8-8 3-3 5 5 12-12 3 3z"
                />
              </svg>
              <h1 class="text-3xl text-slate-800 font-bold mb-8 break-words">
                パスワード再設定メールを<br />送信しました。
              </h1>
              <div>
                メール内のリンク先のページで、<br />パスワードの再設定を完了してください。
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </ModalLayout>
</template>

<script>
import { ref } from 'vue';
import UserService from '../services/UserService';
import { openAlertModal } from '@/stores/AlertModalStore';
import ModalLayout from '@/components-new/common/containers/ModalLayout.vue';

export default {
  name: 'RequestResetPassword',
  components: {
    ModalLayout,
  },
  setup() {
    const isMailSent = ref(false);
    const email = ref('');

    const requestResetPassword = async () => {
      if (email.value === '') {
        openAlertModal({ body: 'メールアドレスを入力してください' });
        return;
      }
      try {
        await UserService.requestResetPassword(email.value);
        isMailSent.value = true;
      } catch (e) {
        openAlertModal({
          body: '有効なメールアドレスではないか、登録されていないメールアドレスです',
        });
        return;
      }
      return;
    };

    return {
      email,
      isMailSent,
      requestResetPassword,
    };
  },
};
</script>
