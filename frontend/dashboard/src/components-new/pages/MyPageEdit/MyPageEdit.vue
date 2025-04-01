<template>
  <PageLayout>
    <div class="flex">
      <div
        id="drawing"
        class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden"
      >
        <main class="h-full">
          <div
            class="h-full px-4 sm:px-6 lg:px-8 py-8 w-full max-w-9xl mx-auto"
          >
            <!-- Cards -->
            <div class="h-full flex justify-center items-center">
              <div class="max-w-2xl w-full mx-auto col-span-12">
                <div
                  class="h-full flex flex-col col-span-4 bg-white shadow-lg rounded-md"
                >
                  <div class="p-6">
                    <section class="">
                      <div class="flex justify-between items-center mb-8">
                        <h2 class="text-2xl font-bold mb-2">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="1em"
                            viewBox="0 0 448 512"
                            class="w-5 h-5 inline mr-3"
                            fill="#005DA8"
                          >
                            <path
                              d="M224 256c70.7 0 128-57.3 128-128S294.7 0 224 0 96 57.3 96 128s57.3 128 128 128zm89.6 32h-16.7c-22.2 10.2-46.9 16-72.9 16s-50.6-5.8-72.9-16h-16.7C60.2 288 0 348.2 0 422.4V464c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48v-41.6c0-74.2-60.2-134.4-134.4-134.4z"
                            />
                          </svg>
                          マイページ
                        </h2>
                      </div>
                      <form action="">
                        <div class="max-w-md w-full mx-auto px-5">
                          <div class="grid grid-cols-12 items-center mb-7">
                            <label
                              class="col-span-5 block text-sm font-medium"
                              for="name"
                              >担当者名</label
                            >
                            <p class="col-span-7">{{ userName }}</p>
                          </div>
                          <div class="grid grid-cols-12 items-center mb-7">
                            <label
                              class="col-span-5 block text-sm font-medium"
                              for="company"
                              >会社名</label
                            >
                            <p class="col-span-7">{{ userCompany }}</p>
                          </div>
                          <div class="grid grid-cols-12 items-center mb-7">
                            <label 
                              class="col-span-5 block text-sm font-medium"
                              for="affiliation"
                              >部署名</label
                            >
                            <p class="col-span-7">{{  userAffiliation }}</p>
                          </div>
                          <div class="grid grid-cols-12 items-center mb-7">
                            <label
                              class="col-span-5 block text-sm font-medium"
                              for="email"
                              >ログインID</label
                            >
                            <p class="col-span-7">{{ userMail }}</p>
                          </div>
                          <div class="grid grid-cols-12 items-center mb-7">
                            <label
                              class="col-span-5 block text-sm font-medium"
                              for="current_password"
                              >現在のパスワード</label
                            >
                            <div class="relative col-span-7 w-full">
                              <input
                                id="current_password"
                                v-model="current_password"
                                class="form-input w-full"
                                :type="showPassword1 ? 'text' : 'password'"
                                autocomplete="new-password"
                              />
                              <label
                                for="password1_sh"
                                class="h-4 absolute my-auto inset-y-1/2 right-2 cursor-pointer peer"
                              >
                                <input
                                  id="password1_sh"
                                  v-model="showPassword1"
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
                              for="new_password"
                              >新しいパスワード</label
                            >
                            <div class="relative col-span-7 w-full">
                              <input
                                id="new_password"
                                v-model="new_password"
                                class="col-span-7 form-input w-full"
                                :type="showPassword2 ? 'text' : 'password'"
                              />
                              <label
                                for="password2_sh"
                                class="h-4 absolute my-auto inset-y-1/2 right-2 cursor-pointer peer"
                              >
                                <input
                                  id="password2_sh"
                                  v-model="showPassword2"
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
                              >新しいパスワードの確認</label
                            >
                            <div class="relative col-span-7 w-full">
                              <input
                                id="retype"
                                v-model="retype"
                                class="col-span-7 form-input w-full"
                                :type="showPassword3 ? 'text' : 'password'"
                              />
                              <label
                                for="password3_sh"
                                class="h-4 absolute my-auto inset-y-1/2 right-2 cursor-pointer peer"
                              >
                                <input
                                  id="password3_sh"
                                  v-model="showPassword3"
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

                        <div class="mx-16 mb-6">
                          <div class="text-red-500 text-xs md:text-sm">
                            パスワードは英大文字、英小文字、数字、記号をすべての種類最低1文字以上づつ含んだ形で組み合わせ、12
                            文字から 16
                            文字のパスワードを設定してください。また，記号は、次の
                            1 つ以上を含むようにしてください。: @ # $ % ^ &amp;
                            * - _ + = [ ] { } | \ : ' , ? / ` ~ " ( ) ; .
                          </div>
                        </div>

                        <div class="text-center mb-7">
                          <button
                            class="btn-sm text-[16px] bg-neutral-500 text-white hover:bg-gray-300 w-[152px] h-[42px] border-slate-200 hover:border-slate-300 rounded shadow-md mr-[32px]"
                            @click.prevent="onCancel"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              height="1em"
                              viewBox="0 0 448 512"
                              class="w-5 h-5 inline mr-3"
                              fill="#FFFFFF"
                            >
                              <path
                                d="M257.5 445.1l-22.2 22.2c-9.4 9.4-24.6 9.4-33.9 0L7 273c-9.4-9.4-9.4-24.6 0-33.9L201.4 44.7c9.4-9.4 24.6-9.4 33.9 0l22.2 22.2c9.5 9.5 9.3 25-.4 34.3L136.6 216H424c13.3 0 24 10.7 24 24v32c0 13.3-10.7 24-24 24H136.6l120.5 114.8c9.8 9.3 10 24.8.4 34.3z"
                              />
                            </svg>
                            キャンセル
                          </button>
                          <button
                            class="btn-sm text-[16px] w-[184px] h-[42px] border-slate-200 hover:border-slate-300 hover:bg-gray-50 rounded shadow-md"
                            @click.prevent="onSave"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              height="1em"
                              viewBox="0 0 448 512"
                              class="w-5 h-5 inline mr-3"
                              fill="#005DA8"
                            >
                              <path
                                d="M433.941 129.941l-83.882-83.882A48 48 0 0 0 316.118 32H48C21.49 32 0 53.49 0 80v352c0 26.51 21.49 48 48 48h352c26.51 0 48-21.49 48-48V163.882a48 48 0 0 0-14.059-33.941zM224 416c-35.346 0-64-28.654-64-64 0-35.346 28.654-64 64-64s64 28.654 64 64c0 35.346-28.654 64-64 64zm96-304.52V212c0 6.627-5.373 12-12 12H76c-6.627 0-12-5.373-12-12V108c0-6.627 5.373-12 12-12h228.52c3.183 0 6.235 1.264 8.485 3.515l3.48 3.48A11.996 11.996 0 0 1 320 111.48z"
                              />
                            </svg>
                            保存
                          </button>
                        </div>
                      </form>
                    </section>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import PageLayout from '@components/common/containers/PageLayout.vue';
import UserService, {
  InvalidTokenError,
  InvalidPasswordError,
} from '@/services/UserService';
import { useRoute, useRouter } from 'vue-router';
import { openConfirmModal } from '@/stores/ConfirmModalStore';
import { openAlertModal } from '@/stores/AlertModalStore';

const router = useRouter();
const userId = ref('');
const userName = ref('');
const userCompany = ref('');
const userAffiliation = ref('');
const userMail = ref('');
const showPassword1 = ref(false);
const showPassword2 = ref(false);
const showPassword3 = ref(false);
const current_password = ref('');
const new_password = ref('');
const retype = ref('');
const errors = ref({});

onMounted(async () => {
  const user = await UserService.fetchCurrentUser().catch(() => {
    return;
  });
  userId.value = user?.id ?? '';
  userName.value = user?.username ?? '';
  userCompany.value = user?.company?.name ?? '';
  userAffiliation.value = user?.affiliation ?? '';
  userMail.value = user?.email ?? '';
});
const onCancel = () => {
  openConfirmModal({
    body: '変更内容を破棄しますか？',
    onResponse: (confirmed: boolean) => {
      if (confirmed) {
        router.push('/mypage');
      }
    },
  });
};
const onSave = async () => {
  // if (current_password.value === '') {
  //   openAlertModal({ body: '現在のパスワードを入力してください' });
  //   return;
  // }
  // if (new_password.value === '') {
  //   openAlertModal({ body: '新しいパスワードを入力してください' });
  //   return;
  // }
  // if (retype.value === '') {
  //   openAlertModal({ body: '確認用パスワードを入力してください' });
  //   return;
  // }
  // if (new_password.value !== retype.value) {
  //   openAlertModal({ body: '確認用パスワードが異なります' });
  //   return;
  // }
  
  if (current_password.value === '' || new_password.value === '' || retype.value === '') {
    openAlertModal({ body: '必要な情報をすべて入力してください。' });
    return;
  }
  if (new_password.value !== retype.value) {
    openAlertModal({ body: '確認用パスワードが異なります。' });
    return;
  }

  openConfirmModal({
    body: '変更内容を保存しますか？',
    onResponse: async (confirmed: boolean) => {
      if (confirmed) {
        try {
          await UserService.changePassword({
            current_password: current_password.value,
            new_password: new_password.value,
          });
          router.push('/mypage');
          return;
        } catch (error) {
          if (error instanceof InvalidPasswordError) {
            errors.value = error.errors;
            return;
          } else {
            openAlertModal({ body: '現在のパスワードが異なります。' });
            throw error;
          }
        }
      }
    },
  });
};

</script>
