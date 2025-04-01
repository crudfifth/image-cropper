import { reactive, ref } from 'vue';

export const userCountStore = reactive({
  userLimit: ref<number>(0),
  userCount: ref<number>(0),
  activeUserCount: ref<number>(0),
});
