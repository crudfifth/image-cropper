<template>
  <main class="bg-main-blue">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full md:w-1/2 mx-auto">
        <div class="min-h-screen h-full flex flex-col bg-white after:flex-1">
          <div class="px-4 py-64">
            <div class="max-w-md mx-auto">
              <div class="text-center">
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
                  <!-- NOTE: 一時的にメール認証を無効化している -->
                  <!-- 認証メールを送信しました -->
                  登録が完了しました
                </h1>
                <div>
                  <!-- NOTE: 一時的にメール認証を無効化している -->
                  <!-- メール内のリンクをクリックして、<br />アカウントの登録を完了してください。 -->
                  <router-link
                    class="btn bg-indigo-500 hover:bg-indigo-600 text-white"
                    to="/signin"
                    >ログイン</router-link
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
export default {
  name: 'AuthMailSent',
};
</script>
