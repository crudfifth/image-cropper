<template>
  <PageLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-10xl mx-auto">
      <CSVUploaderLayout />
    </div>
  </PageLayout>
</template>
<script setup lang="ts">
import PageLayout from '@/components-new/common/containers/PageLayout.vue';
import CSVUploaderLayout from './containers/CSVUploaderLayout.vue';
</script>
