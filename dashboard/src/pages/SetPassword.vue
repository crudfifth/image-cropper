<template>
  <ModalLayout>
    <main class="bg-main-blue">
      <div class="relative flex">
        <!-- Content -->
        <div class="w-full md:w-1/2 mx-auto">
          <div class="min-h-screen h-full flex flex-col bg-white after:flex-1">
            <div class="px-4 py-64">
              <div class="max-w-md mx-auto">
                <h1 class="text-3xl text-slate-800 font-bold mb-6">
                  パスワードの設定
                </h1>
                <!-- Form -->
                <form>
                  <div class="mb-8">
                    <div class="grid grid-cols-12 items-center mb-7">
                      <label
                        class="col-span-5 block text-sm font-medium"
                        for="new_password"
                        >パスワード</label
                      >
                      <div class="relative col-span-7 w-full">
                        <input
                          id="new_password"
                          v-model="password"
                          class="col-span-7 form-input w-full"
                          :type="showPassword ? 'text' : 'password'"
                        />
                        <label
                          for="password2_sh"
                          class="h-4 absolute my-auto inset-y-1/2 right-2 cursor-pointer peer"
                        >
                          <input
                            id="password2_sh"
                            v-model="showPassword"
                            class="hidden peer"
                            type="checkbox"
                          />
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="1em"
                            viewBox="0 0 640 512"
                            class="peer-checked:hidden"
                            fill="#848484"
                          >
                            <path
                              d="M320 400c-75.85 0-137.25-58.71-142.9-133.11L72.2 185.82c-13.79 17.3-26.48 35.59-36.72 55.59a32.35 32.35 0 0 0 0 29.19C89.71 376.41 197.07 448 320 448c26.91 0 52.87-4 77.89-10.46L346 397.39a144.13 144.13 0 0 1-26 2.61zm313.82 58.1l-110.55-85.44a331.25 331.25 0 0 0 81.25-102.07 32.35 32.35 0 0 0 0-29.19C550.29 135.59 442.93 64 320 64a308.15 308.15 0 0 0-147.32 37.7L45.46 3.37A16 16 0 0 0 23 6.18L3.37 31.45A16 16 0 0 0 6.18 53.9l588.36 454.73a16 16 0 0 0 22.46-2.81l19.64-25.27a16 16 0 0 0-2.82-22.45zm-183.72-142l-39.3-30.38A94.75 94.75 0 0 0 416 256a94.76 94.76 0 0 0-121.31-92.21A47.65 47.65 0 0 1 304 192a46.64 46.64 0 0 1-1.54 10l-73.61-56.89A142.31 142.31 0 0 1 320 112a143.92 143.92 0 0 1 144 144c0 21.63-5.29 41.79-13.9 60.11z"
                            />
                          </svg>
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="1em"
                            viewBox="0 0 576 512"
                            class="hidden peer-checked:block"
                            fill="#005DA8"
                          >
                            <path
                              d="M572.52 241.4C518.29 135.59 410.93 64 288 64S57.68 135.64 3.48 241.41a32.35 32.35 0 0 0 0 29.19C57.71 376.41 165.07 448 288 448s230.32-71.64 284.52-177.41a32.35 32.35 0 0 0 0-29.19zM288 400a144 144 0 1 1 144-144 143.93 143.93 0 0 1-144 144zm0-240a95.31 95.31 0 0 0-25.31 3.79 47.85 47.85 0 0 1-66.9 66.9A95.78 95.78 0 1 0 288 160z"
                            />
                          </svg>
                        </label>
                      </div>
                    </div>
                    <div class="grid grid-cols-12 items-center mb-7">
                      <label
                        class="col-span-5 block text-sm font-medium"
                        for="retype"
                        >パスワードの確認</label
                      >
                      <div class="relative col-span-7 w-full">
                        <input
                          id="retype"
                          v-model="confirmationPassword"
                          class="col-span-7 form-input w-full"
                          :type="showConfirmationPassword ? 'text' : 'password'"
                        />
                        <label
                          for="password3_sh"
                          class="h-4 absolute my-auto inset-y-1/2 right-2 cursor-pointer peer"
                        >
                          <input
                            id="password3_sh"
                            v-model="showConfirmationPassword"
                            class="hidden peer"
                            type="checkbox"
                          />
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="1em"
                            viewBox="0 0 640 512"
                            class="peer-checked:hidden"
                            fill="#848484"
                          >
                            <path
                              d="M320 400c-75.85 0-137.25-58.71-142.9-133.11L72.2 185.82c-13.79 17.3-26.48 35.59-36.72 55.59a32.35 32.35 0 0 0 0 29.19C89.71 376.41 197.07 448 320 448c26.91 0 52.87-4 77.89-10.46L346 397.39a144.13 144.13 0 0 1-26 2.61zm313.82 58.1l-110.55-85.44a331.25 331.25 0 0 0 81.25-102.07 32.35 32.35 0 0 0 0-29.19C550.29 135.59 442.93 64 320 64a308.15 308.15 0 0 0-147.32 37.7L45.46 3.37A16 16 0 0 0 23 6.18L3.37 31.45A16 16 0 0 0 6.18 53.9l588.36 454.73a16 16 0 0 0 22.46-2.81l19.64-25.27a16 16 0 0 0-2.82-22.45zm-183.72-142l-39.3-30.38A94.75 94.75 0 0 0 416 256a94.76 94.76 0 0 0-121.31-92.21A47.65 47.65 0 0 1 304 192a46.64 46.64 0 0 1-1.54 10l-73.61-56.89A142.31 142.31 0 0 1 320 112a143.92 143.92 0 0 1 144 144c0 21.63-5.29 41.79-13.9 60.11z"
                            />
                          </svg>
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="1em"
                            viewBox="0 0 576 512"
                            class="hidden peer-checked:block"
                            fill="#005DA8"
                          >
                            <path
                              d="M572.52 241.4C518.29 135.59 410.93 64 288 64S57.68 135.64 3.48 241.41a32.35 32.35 0 0 0 0 29.19C57.71 376.41 165.07 448 288 448s230.32-71.64 284.52-177.41a32.35 32.35 0 0 0 0-29.19zM288 400a144 144 0 1 1 144-144 143.93 143.93 0 0 1-144 144zm0-240a95.31 95.31 0 0 0-25.31 3.79 47.85 47.85 0 0 1-66.9 66.9A95.78 95.78 0 1 0 288 160z"
                            />
                          </svg>
                        </label>
                      </div>
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
                      設定
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </ModalLayout>
</template>
<script setup lang="ts">
import ModalLayout from '@/components-new/common/containers/ModalLayout.vue';
import UserService from '@/services/UserService';
import { openAlertModal } from '@/stores/AlertModalStore';
import { PropType, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

defineProps({
  options: {
    type: Array as PropType<string[]>,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
});

defineEmits(['update:modelValue']);

const password = ref('');
const showPassword = ref(false);
const confirmationPassword = ref('');
const showConfirmationPassword = ref(false);

const route = useRoute();
const router = useRouter();
onMounted(async () => {
  const uid = route.query.uid;
  const token = route.query.token;
  if (!uid || !token) {
    openAlertModal({ body: 'URLが不正です' });
    router.push('/');
    return;
  }
});

const onSubmit = async () => {
  if (password.value !== confirmationPassword.value) {
    openAlertModal({ body: 'パスワードが一致しません' });
    return;
  }
  if (route.query.uid && route.query.token) {
    try {
      const updatedUser = await UserService.setPassword(
        password.value,
        String(route.query.uid),
        String(route.query.token)
      );
      await UserService.signIn({
        email: updatedUser.email,
        password: password.value,
      });
      router.push({ name: 'setUserInfo' });
    } catch (e) {
      openAlertModal({ body: 'パスワードの設定に失敗しました' });
      return;
    }
  }
};
</script>
