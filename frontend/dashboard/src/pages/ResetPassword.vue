<template>
  <ModalLayout>
    <main class="bg-main-blue">
      <div class="relative flex">
        <!-- Content -->
        <div class="w-full">
          <div class="min-h-screen h-full flex flex-col justify-center">
            <div class="max-w-md mx-auto px-4 py-8 bg-white rounded">
              <h1 class="text-3xl text-slate-800 font-bold mb-6">
                パスワード再設定
              </h1>
              <!-- Form -->
              <form>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="password"
                      >新しいパスワード<span class="text-rose-500"
                        >*</span
                      ></label
                    >
                    <input
                      id="password"
                      v-model="password"
                      class="form-input w-full mb-2"
                      :type="showPassword ? 'text' : 'password'"
                    />
                    <label class="cursor-pointer">
                      <input
                        v-model="showPassword"
                        class="cursor-pointer"
                        type="checkbox"
                      />
                      パスワードを表示
                    </label>
                  </div>
                  <div>
                    <ul>
                      <li v-for="error in errors" class="text-sm text-rose-500">
                        {{ error }}
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="flex justify-end mt-6">
                  <button
                    class="btn bg-indigo-500 hover:bg-indigo-600 text-white whitespace-nowrap"
                    @click.prevent="resetPassword"
                  >
                    保存
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </main>
  </ModalLayout>
</template>

<script>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import UserService, {
  InvalidPasswordError,
  InvalidTokenError,
} from '../services/UserService';
import { openAlertModal } from '@/stores/AlertModalStore';
import ModalLayout from '@/components-new/common/containers/ModalLayout.vue';

export default {
  name: 'ResetPassword',
  components: {
    ModalLayout,
  },
  setup() {
    const password = ref('');
    const route = useRoute();
    const router = useRouter();

    const errors = ref([]);
    const showPassword = ref(false);

    const resetPassword = async () => {
      if (password.value === '') {
        openAlertModal({ body: 'パスワードを入力してください' });
        return;
      }
      const token = route.query.token;
      try {
        await UserService.resetPassword({ token, password: password.value });
        openAlertModal({ body: 'パスワードを変更しました' });
        router.push('/');
        return;
      } catch (error) {
        if (error instanceof InvalidTokenError) {
          openAlertModal({
            body: '無効なパスワード再設定リンクです。再度パスワード再設定をお願いします。',
          });
          router.push('/');
          return;
        } else if (error instanceof InvalidPasswordError) {
          errors.value = error.errors;
          return;
        } else {
          openAlertModal({ body: '予期せぬエラーが発生しました。' });
          throw error;
        }
      }
    };

    return {
      password,
      errors,
      showPassword,
      resetPassword,
    };
  },
};
</script>
