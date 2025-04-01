<template>
  <header class="fixed inset-x-0 top-0 bg-transparent z-30">
    <div class="flex flex-row-reverse justify-between items-end p-2 mx-4">
      <LanguageSelector />
    </div>
  </header>
</template>

<script setup lang="ts">
import LanguageSelector from '../presenters/composites/LanguageSelector.vue';
</script>
