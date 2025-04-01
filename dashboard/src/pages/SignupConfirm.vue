<template>
  <main class="bg-main-blue">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full md:w-1/2 mx-auto">
        <div class="min-h-screen h-full flex flex-col bg-white after:flex-1">
          <div class="flex-1">
            <!-- Progress bar -->
            <div class="px-4 pt-12 pb-8">
              <div class="max-w-md mx-auto w-full">
                <div class="relative">
                  <div
                    class="absolute left-0 top-1/2 -mt-px w-full h-0.5 bg-slate-200"
                    aria-hidden="true"
                  ></div>
                  <ul class="relative flex justify-between w-full">
                    <li>
                      <router-link
                        class="flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold bg-indigo-500 text-white"
                        to="/onboarding-01"
                        >1</router-link
                      >
                    </li>
                    <li>
                      <router-link
                        class="flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold bg-indigo-500 text-white"
                        to="/onboarding-02"
                        >2</router-link
                      >
                    </li>
                    <li>
                      <router-link
                        class="flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold bg-slate-100 text-slate-500"
                        to="/onboarding-03"
                        >3</router-link
                      >
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="px-4 py-8">
            <div class="max-w-md mx-auto">
              <h1 class="text-3xl text-slate-800 font-bold mb-5">
                ユーザー登録
              </h1>
              <h2 class="text-xl mb-6">入力内容確認</h2>
              <!-- Form -->
              <form>
                <div class="mb-8">
                  <div class="mb-5">
                    <label class="block text-sm font-medium mb-1" for="default"
                      >名前</label
                    >
                    <p id="default" class="ml-3">{{ formData.name }}</p>
                  </div>
                  <div class="mb-5">
                    <label class="block text-sm font-medium mb-1" for="default"
                      >メールアドレス</label
                    >
                    <p id="default" class="ml-3">{{ formData.email }}</p>
                  </div>
                  <div class="mb-5">
                    <label class="block text-sm font-medium mb-1" for="default"
                      >パスワード</label
                    >
                    <p id="default" class="ml-3">
                      ※セキュリティ上の観点から表示されません
                    </p>
                  </div>
                </div>
                <div class="flex items-center justify-between">
                  <button
                    class="text-sm underline hover:no-underline"
                    @click="$emit('back')"
                  >
                    戻る
                  </button>
                  <button
                    class="btn bg-indigo-500 hover:bg-indigo-600 text-white ml-auto"
                    @click.prevent="$emit('confirm')"
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
export default {
  name: 'SignupConfirm',
  props: {
    formData: {
      type: Object,
      required: true,
    },
  },
};
</script>
