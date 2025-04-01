<template>
  <ModalLayout>
    <SignupForm
      v-if="!isCompleted"
      :password-errors="passwordErrors"
      @submit="onSubmitInput"
    />
    <AuthMailSent v-else />
  </ModalLayout>
</template>

<script>
import { ref, reactive } from 'vue';
import SignupForm from './SignupForm.vue';
import SignupConfirm from './SignupConfirm.vue';
import AuthMailSent from './AuthMailSent.vue';
import UserService, {
  UserConflictError,
  InvalidPasswordError,
} from '../services/UserService';
import { openAlertModal } from '@/stores/AlertModalStore';
import ModalLayout from '@/components-new/common/containers/ModalLayout.vue';

export default {
  name: 'SignupContainer',
  components: {
    SignupForm,
    SignupConfirm,
    AuthMailSent,
    ModalLayout,
  },
  setup() {
    const isCompleted = ref(false);
    const passwordErrors = ref([]);

    const onSubmitInput = async (data) => {
      try {
        await UserService.signup({
          username: data.name,
          email: data.email,
          password: data.password,
        });
        isCompleted.value = true;
      } catch (error) {
        if (error instanceof UserConflictError) {
          openAlertModal({
            body: 'このメールアドレスは既に登録されています。',
          });
        } else if (error instanceof InvalidPasswordError) {
          passwordErrors.value = error.errors;
        } else {
          openAlertModal({ body: '予期せぬエラーが発生しました。' });
        }
      }
    };

    return {
      isCompleted,
      passwordErrors,
      onSubmitInput,
    };
  },
};
</script>
