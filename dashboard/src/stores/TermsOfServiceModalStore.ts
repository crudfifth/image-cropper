import { ref } from 'vue';

const DEFAULT_TITLE = '利用規約';

export const isTermsModalOpen = ref(false);
export const termsTitle = ref(DEFAULT_TITLE);
export const termsBody = ref('');

// モーダルを開く関数
export const openTermsModal = ({
  body,
  title = DEFAULT_TITLE,
}: {
  body: string;
  title?: string;
}) => {
  termsTitle.value = title;
  termsBody.value = body;
  isTermsModalOpen.value = true;
};

// モーダルを閉じる関数
export const closeTermsModal = () => {
  termsTitle.value = DEFAULT_TITLE;
  termsBody.value = '';
  isTermsModalOpen.value = false;
};
