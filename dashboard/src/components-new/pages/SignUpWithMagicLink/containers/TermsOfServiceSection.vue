<template>
  <h1 class="text-2xl font-bold">ご利用規約</h1>
  <div class="flex flex-col items-center gap-4 my-4">
    <div class="mx-6 overflow-auto h-[50vh] border-2 border-gray-200">
      <!-- Markdown本文のスタイルを変更したい時は、css/additional-styles/markdown.cssを編集すること -->
      <TermsOfServiceMarkdown class="m-6" />
    </div>

    <div class="flex items-center mt-2">
      <input id="agree-terms-of-service" v-model="isAgree" type="checkbox" />
      <label for="agree-terms-of-service" class="ml-2"
        >利用規約に同意する
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import TermsOfServiceMarkdown from '@/text-resources/ihi-biz-terms-of-service.md';
const isAgree = defineModel<boolean>();
</script>
