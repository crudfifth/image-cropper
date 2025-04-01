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
                  ユーザー名の登録
                </h1>
                <!-- Form -->
                <form>
                  <div class="mb-8">
                    <div class="mb-5">
                      <label
                        class="block text-sm font-medium mb-1"
                        for="default"
                        >企業</label
                      >
                      <div>{{ user?.company.name }}</div>
                    </div>
                    <div class="mb-5">
                      <label
                        class="block text-sm font-medium mb-1"
                        for="default"
                        >メールアドレス</label
                      >
                      <div>{{ user?.email }}</div>
                    </div>
                    <div class="mb-5">
                      <label
                        class="block text-sm font-medium mb-1"
                        for="default"
                        >名前<span class="text-rose-500">*</span></label
                      >
                      <input
                        v-model.trim="name"
                        class="form-input w-full"
                        type="text"
                        placeholder="名前を入力してください"
                      />
                    </div>
                  </div>
                  <div class="flex items-center justify-between">
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
  </ModalLayout>
</template>

<script setup lang="ts">
import ModalLayout from '@/components-new/common/containers/ModalLayout.vue';
import { User } from '@/repositories/UserRepository';
import UserService from '@/services/UserService';
import { openAlertModal } from '@/stores/AlertModalStore';
import { Ref, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const user: Ref<undefined | User> = ref(undefined);
const name: Ref<string> = ref('');
const router = useRouter();

onMounted(async () => {
  try {
    user.value = await UserService.fetchCurrentUser();
  } catch {
    return;
  }
});

const onSubmit = async () => {
  if (!user.value) {
    return;
  }
  try {
    await UserService.updateUserName(user.value.id, name.value);
    router.push('/');
  } catch {
    openAlertModal({ body: 'ユーザー名の登録に失敗しました' });
    return;
  }
};
</script>
