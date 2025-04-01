<!-- ログイン中のページで使われるレイアウト。サイドナビゲーション+ヘッダーの2ペイン。 -->
<template>
  <ModalLayout>
    <div class="flex h-screen">
      <div class="h-screen">
        <SideNavigation
          :sidebar-open="isSideNavigationOpen"
          @close-sidebar="isSideNavigationOpen = false"
        />
      </div>

      <div
        id="drawing"
        class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden"
      >
        <HeaderNavigation
          :sidebar-open="isSideNavigationOpen"
          @toggle-sidebar="isSideNavigationOpen = !isSideNavigationOpen"
        >
        </HeaderNavigation>
        <main class="flex-1 overflow-y-auto overflow-x-hidden">
          <slot> <!-- ページ固有のコンテンツがここに挿入される --> </slot>
        </main>
        <FooterNavigation />
      </div>
    </div>
  </ModalLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import HeaderNavigation from './HeaderNavigation.vue';
import SideNavigation from './SideNavigation.vue';
import ModalLayout from './ModalLayout.vue';
import FooterNavigation from './FooterNavigation.vue';

const isSideNavigationOpen = ref(false);
</script>
