<template>
  <Transition>
    <button
      v-show="isScrollNeeded"
      key="scrollToTopButton"
      class="fade-enter-active fade-leave-active bg-gray-300 hover:bg-gray-400 text-white font-bold p-2 rounded-full flex items-center justify-center h-12 w-12"
      @click="scrollToTop"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6 mx-auto"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M5 15l7-7 7 7"
        />
      </svg>
    </button>
  </Transition>
</template>
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const isScrollNeeded = ref(false);

const checkScroll = () => {
  isScrollNeeded.value = window.scrollY > 0;
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

onMounted(() => {
  window.addEventListener('scroll', checkScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', checkScroll);
});
</script>

<style scoped>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}
.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
