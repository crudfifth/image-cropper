<template>
  <ModalLayout>
    <div
      id="drawing"
      class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden bg-white"
    >
      <PublicHeaderNavigation />
      <main class="flex-1 overflow-y-auto overflow-x-hidden">
        <slot> <!-- ページ固有のコンテンツがここに挿入される --> </slot>
      </main>
      <PublicFooterNavigation />
    </div>
    <div class="fixed bottom-20 right-5 z-50">
      <ScrollToTopButton />
    </div>
  </ModalLayout>
</template>
<script setup lang="ts">
import ModalLayout from './ModalLayout.vue';
import PublicHeaderNavigation from './PublicHeaderNavigation.vue';
import PublicFooterNavigation from './PublicFooterNavigation.vue';
import ScrollToTopButton from '../presenters/buttons/ScrollToTopButton.vue';
</script>
