import { ref } from 'vue';

const DEFAULT_TITLE = 'IHIダッシュボードからのメッセージ';

export const isAlertModalOpen = ref(false);
export const alertTitle = ref(DEFAULT_TITLE);
export const alertBody = ref('');
export const onResponseCallback = ref<() => void>();

export const openAlertModal = ({
  body,
  title,
  onResponse,
}: {
  body: string;
  title?: string;
  onResponse?: () => void;
}) => {
  if (title) {
    alertTitle.value = title;
  }
  alertBody.value = body;
  isAlertModalOpen.value = true;
  onResponseCallback.value = onResponse;
};

export const closeAlertModal = () => {
  onResponseCallback.value?.();
  alertTitle.value = DEFAULT_TITLE;
  alertBody.value = '';
  isAlertModalOpen.value = false;
  onResponseCallback.value = undefined;
};
