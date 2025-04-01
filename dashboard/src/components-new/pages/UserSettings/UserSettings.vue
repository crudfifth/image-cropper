<template>
  <PageLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-10xl mx-auto">
      <div class="grid grid-cols-12 gap-6">
        <UserSettingLayout />
        <div class="col-span-9 flex flex-col">
          <UserListLayout />
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import PageLayout from '@components/common/containers/PageLayout.vue';
import UserSettingLayout from './containers/UserSettingLayout.vue';
import UserListLayout from './containers/UserListLayout.vue';
</script>
