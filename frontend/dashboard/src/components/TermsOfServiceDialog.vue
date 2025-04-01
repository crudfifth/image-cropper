<template>
  <ModalBlank
    id="tos-modal"
    :modal-open="isModalOpen"
    @close-modal="$emit('close-modal')"
  >
    <!-- センタリングする -->
    <div
      class="m-4 flex flex-col items-center justify-center space-y-4 relative"
    >
      <button
        class="absolute top-0 right-0 m-2 text-2xl"
        @click.stop="$emit('close-modal')"
      >
        ✕
      </button>
      <div class="overflow-auto h-[75vh]">
        <!-- Markdown本文のスタイルを変更したい時は、css/additional-styles/markdown.cssを編集すること -->
        <TermsOfServiceMarkdown class="m-6" />
      </div>

      <div class="flex flex-wrap justify-end space-x-2 mt-12">
        <button
          v-if="onAgree"
          class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 pa-2"
          :disabled="isLoading"
          @click.stop="
            async (event) => {
              if (onAgree) {
                isLoading = true;
                await onAgree(event);
                isLoading = false;
              }
            }
          "
        >
          同意する
        </button>
      </div>
    </div>
  </ModalBlank>
</template>

<script setup lang="ts">
import { ref, PropType } from 'vue';
import ModalBlank from './ModalBlank.vue';
import TermsOfServiceMarkdown from '@/text-resources/ihi-biz-terms-of-service.md';

defineEmits(['close-modal']);

defineProps({
  title: {
    type: String,
    required: true,
  },
  isModalOpen: {
    type: Boolean,
    default: false,
  },
  onAgree: {
    type: Function as PropType<(event: MouseEvent) => Promise<void>>,
    required: false,
    default: undefined,
  },
});

const isLoading = ref(false);
</script>
