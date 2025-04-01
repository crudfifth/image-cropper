import { reactive, ref } from 'vue';

// TODO: ログイン中のユーザー情報は全画面で使う可能性があるので、SessionStorageかどこかに移動する
export const userInfoStore = reactive({
  userId: ref<string | undefined>(undefined),
  userName: ref<string | undefined>(undefined),
});
