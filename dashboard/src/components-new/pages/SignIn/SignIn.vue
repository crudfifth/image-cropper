<template>
  <PublicPageLayout class="overflow-auto">
    <div class="flex flex-col justify-center h-screen">
      <div class="grid grid-rows-10 w-full h-screen justify-items-center">
        <div
          class="flex flex-col justify-center justify-local max-w-3xl w-full row-span-8"
        >
          <DashboardLogo class="mb-8" />
          <SignInSection />
        </div>
      </div>
    </div>
  </PublicPageLayout>
</template>
<script setup lang="ts">
import PublicPageLayout from '@components/common/containers/PublicPageLayout.vue';
import DashboardLogo from '@components/common/presenters/composites/DashboardLogo.vue';
import SignInSection from './containers/SignInSection.vue';
</script>

<style scoped>
/* DashboardLogoが見切れないための調整 */
@media (max-height: 750px) {
  .justify-local {
    justify-content: start;
  }
}
</style>
