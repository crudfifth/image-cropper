<template>
  <PublicPageLayout>
    <div class="flex justify-center">
      <div class="flex flex-col mt-8 mb-24 max-w-4xl w-full">
        <form @submit.prevent>
          <DashboardLogo />
          <hr class="w-full border-2 border-main-blue my-4" />
          <TitleSection />
          <hr class="w-full border-2 border-main-blue my-4" />
          <UserFormSection
            ref="userFormSectionRef"
            v-model:is-valid="userInputIsValid"
          />
          <hr class="w-full border-2 border-main-blue my-4" />
          <TermsOfServiceSection
            v-model="isTermsOfServiceAgreed"
            class="my-4"
          />
          <hr class="w-full border-2 border-main-blue my-4" />
          <div class="flex justify-center my-8">
            <SubmitButton
              :on-click-async="handleSubmit"
              :disabled="!(isTermsOfServiceAgreed && userInputIsValid)"
              class="w-32"
            />
          </div>
        </form>
      </div>
    </div>
  </PublicPageLayout>
</template>

<script setup lang="ts">
import PublicPageLayout from '@components/common/containers/PublicPageLayout.vue';

import DashboardLogo from '@components/common/presenters/composites/DashboardLogo.vue';
import TitleSection from './containers/TitleSection.vue';
import UserFormSection from './containers/UserFormSection.vue';
import TermsOfServiceSection from './containers/TermsOfServiceSection.vue';
import SubmitButton from './presenters/SubmitButton.vue';
import { openAlertModal } from '@/stores/AlertModalStore';

import type { UserFormInputValuesType } from './containers/UserFormSection.vue';

import MagicLinkTokenService from '@/services/MagicLinkTokenService';
import UserService from '@/services/UserService';

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
const route = useRoute();
const router = useRouter();

type UserFormSectionInstance = {
  getUserInputs: () => UserFormInputValuesType | undefined;
  setUserInputs: (newVal: Partial<UserFormInputValuesType>) => void;
};

const userFormSectionRef = ref<UserFormSectionInstance | undefined>(undefined);

const token = ref<string>('');

const userInputIsValid = ref<boolean>(false);
const isTermsOfServiceAgreed = ref<boolean>(false);

onMounted(async () => {
  const queryToken = route.query.token;
  if (typeof queryToken !== 'string') {
    onTokenFailed();
    return;
  }

  const userInfo = await MagicLinkTokenService.fetchUserByActivationToken({
    magicLinkToken: queryToken,
  });

  if (!userInfo.success) {
    onTokenFailed();
    return;
  }

  token.value = queryToken;
  userFormSectionRef.value?.setUserInputs({
    mailAddress: userInfo.data.email,
  });
});

const onTokenFailed = () => {
  openAlertModal({
    body: '招待URLが正しくありません。招待を受け直してください。',
    title: '',
    onResponse: () => {
      router.push('/signin');
    },
  });
};

const handleSubmit = async () => {
  const userInputs = userFormSectionRef.value?.getUserInputs();
  if (!userInputs) {
    return;
  }

  const response = await MagicLinkTokenService.activateUser({
    magicLinkToken: token.value,
    userName: userInputs.userName,
    affiliation: userInputs.affiliation,
    password: userInputs.password,
  });

  if (!response.success) {
    openAlertModal({
      body: 'ユーザー登録時にエラーが発生しました。招待を受け直して下さい。',
      title: '',
    });
    return;
  }

  await UserService.signIn({
    email: userInputs.mailAddress,
    password: userInputs.password,
  });

  router.push('/');
};
</script>
