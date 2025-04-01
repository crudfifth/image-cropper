<template>
  <div class="flex justify-center">
    <nav class="flex" role="navigation" aria-label="Navigation">
      <div class="mr-2">
        <router-link
          v-if="currentPage > 1"
          :to="`?page=${currentPage - 1}`"
          class="inline-flex items-center justify-center rounded leading-5 px-2.5 py-2 bg-white hover:bg-indigo-500 border border-slate-200 text-slate-600 hover:text-white shadow-sm"
        >
          <span class="sr-only">Previous</span><wbr />
          <svg class="h-4 w-4 fill-current" viewBox="0 0 16 16">
            <path d="M9.4 13.4l1.4-1.4-4-4 4-4-1.4-1.4L4 8z" />
          </svg>
        </router-link>
        <div
          v-else
          :to="`?page=${currentPage - 1}`"
          class="inline-flex items-center justify-center rounded leading-5 px-2.5 py-2 bg-white border border-slate-200 text-slate-300"
        >
          <span class="sr-only">Previous</span><wbr />
          <svg class="h-4 w-4 fill-current" viewBox="0 0 16 16">
            <path d="M9.4 13.4l1.4-1.4-4-4 4-4-1.4-1.4L4 8z" />
          </svg>
        </div>
      </div>
      <ul class="inline-flex text-sm font-medium -space-x-px shadow-sm">
        <li v-for="n in pageCount" :key="n">
          <div
            v-if="n === currentPage"
            class="inline-flex items-center justify-center leading-5 px-3.5 py-2 bg-white border border-slate-200 text-indigo-500"
          >
            {{ n }}
          </div>
          <router-link
            v-else
            class="inline-flex items-center justify-center leading-5 px-3.5 py-2 bg-white hover:bg-indigo-500 border border-slate-200 text-slate-600 hover:text-white"
            :to="`?page=${n}`"
            >{{ n }}</router-link
          >
        </li>
      </ul>
      <div class="ml-2">
        <router-link
          v-if="currentPage < pageCount"
          :to="`?page=${currentPage + 1}`"
          class="inline-flex items-center justify-center rounded leading-5 px-2.5 py-2 bg-white hover:bg-indigo-500 border border-slate-200 text-slate-600 hover:text-white shadow-sm"
        >
          <span class="sr-only">Next</span><wbr />
          <svg class="h-4 w-4 fill-current" viewBox="0 0 16 16">
            <path d="M6.6 13.4L5.2 12l4-4-4-4 1.4-1.4L12 8z" />
          </svg>
        </router-link>
        <div
          v-else
          :to="`?page=${currentPage + 1}`"
          class="inline-flex items-center justify-center rounded leading-5 px-2.5 py-2 bg-white border border-slate-200 text-slate-300"
        >
          <span class="sr-only">Next</span><wbr />
          <svg class="h-4 w-4 fill-current" viewBox="0 0 16 16">
            <path d="M6.6 13.4L5.2 12l4-4-4-4 1.4-1.4L12 8z" />
          </svg>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
import { onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'PaginationNumeric',
  props: {
    pageCount: {
      type: Number,
      required: true,
    },
    currentPage: {
      type: Number,
      required: true,
    },
  },
  setup: (props, context) => {
    const route = useRoute();

    onMounted(() => setPage());

    watch(route, () => setPage());

    const setPage = () => {
      const page = route.query.page;
      if (page) {
        context.emit('update-current-page', parseInt(page, 10));
      }
    };

    return {};
  },
};
</script>
