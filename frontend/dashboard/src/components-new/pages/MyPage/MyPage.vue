<template>
  <PageLayout>
    <div class="flex">
      <!-- Content area -->
      <div
        id="drawing"
        class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden"
      >
        <main class="h-full">
          <div
            class="h-full px-4 sm:px-6 lg:px-8 py-8 w-full max-w-9xl mx-auto"
          >
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
                        <router-link
                          to="/mypage-edit"
                          class="flex items-center gap-1 text-sm bg-white mr-2 py-2 px-4 border-2 rounded-md"
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="1em"
                            viewBox="0 0 576 512"
                            class="w-5 h-5 inline mr-3"
                            fill="#005DA8"
                          >
                            <path
                              d="M402.6 83.2l90.2 90.2c3.8 3.8 3.8 10 0 13.8L274.4 405.6l-92.8 10.3c-12.4 1.4-22.9-9.1-21.5-21.5l10.3-92.8L388.8 83.2c3.8-3.8 10-3.8 13.8 0zm162-22.9l-48.8-48.8c-15.2-15.2-39.9-15.2-55.2 0l-35.4 35.4c-3.8 3.8-3.8 10 0 13.8l90.2 90.2c3.8 3.8 10 3.8 13.8 0l35.4-35.4c15.2-15.3 15.2-40 0-55.2zM384 346.2V448H64V128h229.8c3.2 0 6.2-1.3 8.5-3.5l40-40c7.6-7.6 2.2-20.5-8.5-20.5H48C21.5 64 0 85.5 0 112v352c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48V306.2c0-10.7-12.9-16-20.5-8.5l-40 40c-2.2 2.3-3.5 5.3-3.5 8.5z"
                            />
                          </svg>
                          編集する
                        </router-link>
                      </div>
                      <div class="max-w-md w-full mx-auto mb-8 p-5">
                        <div class="grid grid-cols-12 items-center mb-7">
                          <label
                            class="col-span-5 block text-sm font-medium"
                            for="name"
                            >担当者名</label
                          >
                          <p class="col-span-7 font-bold">{{ userName }}</p>
                        </div>
                        <div class="grid grid-cols-12 items-center mb-7">
                          <label
                            class="col-span-5 block text-sm font-medium"
                            for="name"
                            >会社名</label
                          >
                          <p class="col-span-7 font-bold">{{ userCompany }}</p>
                        </div>
                        <div class="grid grid-cols-12 items-center mb-7">
                            <label
                              class="col-span-5 block text-sm font-medium"
                              for="affiliation"
                              >部署名</label
                            >
                            <p class="col-span-7 font-bold">{{ displayUserAffiliation }}</p>
                          </div>
                        <div class="grid grid-cols-12 items-center mb-7">
                          <label
                            class="col-span-5 block text-sm font-medium"
                            for="name"
                            >ログインID</label
                          >
                          <p class="col-span-7 font-bold">{{ userMail }}</p>
                        </div>
                        <div class="grid grid-cols-12 items-center mb-7">
                          <label
                            class="col-span-5 block text-sm font-medium"
                            for="name"
                            >パスワード</label
                          >
                          <p class="col-span-7 font-bold">************</p>
                        </div>
                      </div>
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
import { ref, onMounted, computed } from 'vue';
import PageLayout from '@components/common/containers/PageLayout.vue';
import UserService from '@/services/UserService';

const userId = ref('');
const userName = ref('');
const userCompany = ref('');
const userMail = ref('');
const userAffiliation = ref('');

const displayUserAffiliation = computed(() => userAffiliation.value ?? "");

onMounted(async () => {
  const user = await UserService.fetchCurrentUser();
  userId.value = user.id;
  userName.value = user.username;
  userCompany.value = user.company.name;
  userMail.value = user.email;
  userAffiliation.value = user.affiliation ?? '';
});
</script>
