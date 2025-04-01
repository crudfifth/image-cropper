import { ref } from 'vue';

const DEFAULT_TITLE = 'IHIダッシュボードからのメッセージ';

export const isConfirmModalOpen = ref(false);
export const confirmTitle = ref(DEFAULT_TITLE);
export const confirmBody = ref('');
export const onResponseCallback = ref<((result: boolean) => void) | null>(null);

export const openConfirmModal = ({
  body,
  title,
  onResponse,
}: {
  body: string;
  title?: string;
  onResponse?: (confirmed: boolean) => void;
}) => {
  if (title) {
    confirmTitle.value = title;
  }
  confirmBody.value = body;
  isConfirmModalOpen.value = true;
  onResponseCallback.value = onResponse || null;
};

export const closeConfirmModal = (confirmed = false) => {
  if (onResponseCallback.value) {
    onResponseCallback.value(confirmed);
  }
  confirmTitle.value = DEFAULT_TITLE;
  confirmBody.value = '';
  isConfirmModalOpen.value = false;
  onResponseCallback.value = null;
};
