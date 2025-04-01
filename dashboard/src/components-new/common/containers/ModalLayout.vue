<!-- <template>
  <ConfirmModal v-if="isConfirmModalOpen" />
  <AlertModal v-if="isAlertModalOpen" />
  <TermsOfServiceModal
    v-if="isTermsModalOpen"
    :isModalOpen="isTermsModalOpen"
    :title="termsTitle"
    @close-modal="closeTermsModal"
  />
  <slot></slot>
</template>

<script setup lang="ts">
import { isAlertModalOpen } from '@/stores/AlertModalStore';
import AlertModal from '../presenters/modals/AlertModal.vue';
import ConfirmModal from '../presenters/modals/ConfirmModal.vue';
import { isConfirmModalOpen } from '@/stores/ConfirmModalStore';
import TermsOfServiceModal from '../presenters/modals/TermsOfServiceModal.vue';
import { isTermsModalOpen, termsTitle, closeTermsModal } from '@/stores/TermsOfServiceModalStore';
</script> -->
<template>
  <ConfirmModal v-if="isConfirmModalOpen" />
  <AlertModal v-if="isAlertModalOpen" />
  <TermsOfServiceModal
    v-if="isTermsModalOpen"
    :isModalOpen="isTermsModalOpen"
    :title="termsTitle"
    />
    <!-- @close-modal="closeTermsModal" -->
  <slot></slot>
</template>

<script setup lang="ts">
import { isAlertModalOpen } from '@/stores/AlertModalStore';
import AlertModal from '../presenters/modals/AlertModal.vue';
import ConfirmModal from '../presenters/modals/ConfirmModal.vue';
import { isConfirmModalOpen } from '@/stores/ConfirmModalStore';
import TermsOfServiceModal from '../presenters/modals/TermsOfServiceModal.vue';
import { isTermsModalOpen, termsTitle, termsBody } from '@/stores/TermsOfServiceModalStore';
import { ref } from 'vue';

// function closeTermsModal() {
//   isTermsModalOpen.value = true;
// }
</script>
