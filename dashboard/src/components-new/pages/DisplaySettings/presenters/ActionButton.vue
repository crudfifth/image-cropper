<!-- TODO: 使わなくなったので削除 -->
<template>
  <div class="flex col-span-full justify-between">
    <div class="flex items-center"></div>

    <div class="flex gap-2">
      <!-- TODO: 初期実装のスコープ外のため一時的にコメントアウト -->
      <!-- <button
        id="print-as-pdf"
        class="flex items-center gap-1 text-sm bg-white hover:bg-blue-500 hover:text-white mr-2 py-2 px-4 border-2 hover:border-transparent rounded"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          class="w-6 h-6"
          fill="#005DA8"
        >
          <path
            d="M3,3v14h5v5h14V8l-7-7H3zm14,5h-6c-1.1,0-2,.9-2,2v6h6c1.1,0,2-.9,2-2V8z"
          />
        </svg>
        コピーする
      </button> -->
      <button
        id="delete"
        class="flex items-center gap-1 text-sm bg-white hover:bg-blue-500 hover:text-white mr-2 py-2 px-4 border-2 hover:border-transparent rounded"
        :disabled="deleteDisabled"
        @click="$emit('delete')"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 448 512"
          class="w-5 h-5 inline mr-3 mb-1"
          fill="#FB2C78"
        >
          <path
            d="M135.2 17.7C140.6 6.8 151.7 0 163.8 0H284.2c12.1 0 23.2 6.8 28.6 17.7L320 32h96c17.7 0 32 14.3 32 32s-14.3 32-32 32H32C14.3 96 0 81.7 0 64S14.3 32 32 32h96l7.2-14.3zM32 128H416V448c0 35.3-28.7 64-64 64H96c-35.3 0-64-28.7-64-64V128zm96 64c-8.8 0-16 7.2-16 16V432c0 8.8 7.2 16 16 16s16-7.2 16-16V208c0-8.8-7.2-16-16-16zm96 0c-8.8 0-16 7.2-16 16V432c0 8.8 7.2 16 16 16s16-7.2 16-16V208c0-8.8-7.2-16-16-16zm96 0c-8.8 0-16 7.2-16 16V432c0 8.8 7.2 16 16 16s16-7.2 16-16V208c0-8.8-7.2-16-16-16z"
          />
        </svg>
        削除する
      </button>
      <!--
      <button
        id="print-as-pdf"
        class="flex items-center gap-1 text-sm bg-white hover:bg-blue-500 hover:text-white mr-2 py-2 px-4 border-2 hover:border-transparent rounded"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
          />
        </svg>
        pdfで出力する
      </button> -->

      <!-- <button
        id="print"
        class="flex items-center gap-1 text-sm bg-white hover:bg-blue-500 hover:text-white py-2 px-4 border-2 hover:border-transparent rounded"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0110.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18m0 0l.229 2.523a1.125 1.125 0 01-1.12 1.227H7.231c-.662 0-1.18-.568-1.12-1.227L6.34 18m11.318 0h1.091A2.25 2.25 0 0021 15.75V9.456c0-1.081-.768-2.015-1.837-2.175a48.055 48.055 0 00-1.913-.247M6.34 18H5.25A2.25 2.25 0 013 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.041 48.041 0 011.913-.247m10.5 0a48.536 48.536 0 00-10.5 0m10.5 0V3.375c0-.621-.504-1.125-1.125-1.125h-8.25c-.621 0-1.125.504-1.125 1.125v3.659M18 10.5h.008v.008H18V10.5zm-3 0h.008v.008H15V10.5z"
          />
        </svg>
        印刷する
      </button> -->
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps({
  deleteDisabled: { type: Boolean, default: false },
});
defineEmits(['delete']);
</script>
