<template>
  <div class="relative inline-flex">
    <button
      ref="trigger"
      class="w-8 h-8 flex items-center justify-center rounded-full"
      :class="{ 'bg-slate-200': dropdownOpen }"
      aria-haspopup="true"
      :aria-expanded="dropdownOpen"
      @click.prevent="dropdownOpen = !dropdownOpen"
    >
      <span class="sr-only">Notifications</span>
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
          d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"
        />
      </svg>
      <div
        class="absolute top-0 right-0 w-2.5 h-2.5 bg-rose-500 border-2 border-white rounded-full"
      ></div>
    </button>
    <transition
      enter-active-class="transition ease-out duration-200 transform"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-out duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-show="dropdownOpen"
        class="origin-top-right z-10 absolute top-full -mr-48 sm:mr-0 min-w-80 bg-white border border-slate-200 py-1.5 rounded shadow-lg overflow-hidden mt-1"
        :class="align === 'right' ? 'right-0' : 'left-0'"
      >
        <div
          class="text-xs font-semibold text-slate-400 uppercase pt-1.5 pb-2 px-4"
        >
          新着お知らせ
        </div>
        <ul
          ref="dropdown"
          @focusin="dropdownOpen = true"
          @focusout="dropdownOpen = false"
        >
          <li
            v-for="notification in notifications"
            :key="notification.id"
            class="border-b border-slate-200 last:border-0"
          >
            <router-link
              class="block py-2 px-4 hover:bg-slate-50"
              :to="`/notice/${notification.id}`"
              @click="dropdownOpen = false"
            >
              <span class="block text-sm mb-2">
                <span class="font-medium text-slate-800"
                  >{{ notification.title }}<br /></span
                >{{ notification.body }}</span
              >
              <span class="block text-xs font-medium text-slate-400">{{
                formatDate(notification.created_at)
              }}</span>
            </router-link>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script>
import { onMounted, onUnmounted, ref } from 'vue';
import { formatDate } from '../utils/Utils';
export default {
  name: 'DropdownNotifications',
  props: {
    align: {
      type: String,
      default: 'left',
    },
    notifications: {
      type: Array,
      default: () => [],
    },
  },
  setup() {
    const dropdownOpen = ref(false);
    const trigger = ref(null);
    const dropdown = ref(null);

    // close on click outside
    const clickHandler = ({ target }) => {
      if (
        !dropdownOpen.value ||
        dropdown.value.contains(target) ||
        trigger.value.contains(target)
      )
        return;
      dropdownOpen.value = false;
    };

    // close if the esc key is pressed
    const keyHandler = ({ keyCode }) => {
      if (!dropdownOpen.value || keyCode !== 27) return;
      dropdownOpen.value = false;
    };

    onMounted(() => {
      document.addEventListener('click', clickHandler);
      document.addEventListener('keydown', keyHandler);
    });

    onUnmounted(() => {
      document.removeEventListener('click', clickHandler);
      document.removeEventListener('keydown', keyHandler);
    });

    return {
      dropdownOpen,
      trigger,
      dropdown,
      formatDate,
    };
  },
};
</script>
