<template>
  <main class="bg-main-blue">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full md:w-1/2 mx-auto">
        <div class="min-h-screen h-full flex flex-col bg-white after:flex-1">
          <div class="px-4 py-32">
            <div class="max-w-md mx-auto">
              <div v-if="isValid" class="text-center">
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
                <h1 class="text-3xl text-slate-800 font-bold mb-8">
                  ご登録完了しました
                </h1>
                <router-link
                  class="btn bg-indigo-500 hover:bg-indigo-600 text-white"
                  to="/signin"
                  >ログイン</router-link
                >
              </div>
              <div v-else-if="isValid === false" class="text-center">
                <h1 class="text-3xl text-slate-800 font-bold mb-6">
                  無効な認証リンクです
                </h1>
                <div>再度ユーザ登録を行ってください。</div>
                <router-link
                  class="btn bg-indigo-500 hover:bg-indigo-600 text-white mt-8"
                  to="/signup"
                  >ユーザ登録へ</router-link
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import UserService from '../services/UserService';

export default {
  name: 'VerifyEmail',
  setup() {
    const route = useRoute();
    const isValid = ref(undefined);

    onMounted(async () => {
      const activationToken = route.params.token;
      try {
        await UserService.activate(activationToken);
        isValid.value = true;
      } catch (error) {
        isValid.value = false;
      }
    });
    return {
      isValid,
    };
  },
};
</script>
