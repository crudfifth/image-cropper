<!-- ログイン中のページで使われるレイアウト。サイドナビゲーション+ヘッダーの2ペイン。 -->
<template>
  <div class="flex">
    <SideNavigation
      :sidebar-open="isSideNavigationOpen"
      @close-sidebar="isSideNavigationOpen = false"
    />
    <div
      id="drawing"
      class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden"
    >
      <HeaderNavigation
        :sidebar-open="isSideNavigationOpen"
        @toggle-sidebar="isSideNavigationOpen = !isSideNavigationOpen"
      >
      </HeaderNavigation>
      <main>
        <slot> <!-- ページ固有のコンテンツがここに挿入される --> </slot>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import HeaderNavigation from '@/components/navigations/HeaderNavigation.vue';
import SideNavigation from '@/components/navigations/SideNavigation.vue';

const isSideNavigationOpen = ref(false);
</script>
