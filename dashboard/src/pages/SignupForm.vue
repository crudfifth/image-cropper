<template>
  <main class="bg-main-blue">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full md:w-1/2 mx-auto">
        <div class="min-h-screen h-full flex flex-col bg-white after:flex-1">
          <div class="px-4 py-64">
            <div class="max-w-md mx-auto">
              <h1 class="text-3xl text-slate-800 font-bold mb-6">
                ユーザー登録
              </h1>
              <!-- Form -->
              <form>
                <div class="mb-8">
                  <div class="mb-5">
                    <label class="block text-sm font-medium mb-1" for="default"
                      >名前<span class="text-rose-500">*</span></label
                    >
                    <input
                      v-model.trim="name"
                      class="form-input w-full"
                      type="text"
                      placeholder="山田太郎"
                    />
                  </div>
                  <div class="mb-5">
                    <label class="block text-sm font-medium mb-1" for="default"
                      >メールアドレス<span class="text-rose-500">*</span></label
                    >
                    <input
                      v-model.trim="email"
                      class="form-input w-full"
                      type="text"
                      placeholder="sample@sample.mail"
                    />
                  </div>
                  <div class="mb-5">
                    <label class="block text-sm font-medium mb-1" for="default"
                      >パスワード<span class="text-rose-500">*</span></label
                    >
                    <input
                      v-model.trim="password"
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
                      <li
                        v-for="error in passwordErrors"
                        class="text-sm text-rose-500"
                      >
                        {{ error }}
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="flex items-center justify-between">
                  <router-link
                    class="text-sm underline hover:no-underline"
                    to="/"
                    >戻る</router-link
                  >
                  <button
                    class="btn bg-indigo-500 hover:bg-indigo-600 text-white ml-auto"
                    @click.prevent="onSubmit"
                  >
                    登録
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { openAlertModal } from '@/stores/AlertModalStore';
import { ref } from 'vue';

export default {
  name: 'SignupForm',
  props: {
    passwordErrors: {
      type: Array,
      default: () => [],
    },
  },
  setup(props, context) {
    const name = ref('');
    const email = ref('');
    const password = ref('');

    const isEmptyName = ref(undefined);
    const isEmptyEmail = ref(undefined);
    const isEmptyPassword = ref(undefined);
    const showPassword = ref(false);

    const onSubmit = () => {
      isEmptyName.value = name.value === '' ? true : false;
      isEmptyEmail.value = email.value === '' ? true : false;
      isEmptyPassword.value = password.value === '' ? true : false;
      if (isEmptyName.value || isEmptyEmail.value || isEmptyPassword.value) {
        openAlertModal({ body: '必須項目を入力してください' });
        return;
      }
      context.emit('submit', {
        name: name.value,
        email: email.value,
        password: password.value,
      });
    };

    return {
      name,
      email,
      password,
      isEmptyName,
      isEmptyEmail,
      isEmptyPassword,
      showPassword,
      onSubmit,
    };
  },
};
</script>
