<template>
  <div class="relative inline-flex">
    <button
      ref="trigger"
      class="inline-flex justify-center items-center group"
      aria-haspopup="true"
      :aria-expanded="dropdownOpen"
      @click.prevent="dropdownOpen = !dropdownOpen"
    >
      <div class="flex items-center justify-center truncate">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          height="1em"
          viewBox="0 0 448 512"
          class="w-5 h-5 inline"
          fill="#005DA8"
        >
          <path
            d="M224 256c70.7 0 128-57.3 128-128S294.7 0 224 0 96 57.3 96 128s57.3 128 128 128zm89.6 32h-16.7c-22.2 10.2-46.9 16-72.9 16s-50.6-5.8-72.9-16h-16.7C60.2 288 0 348.2 0 422.4V464c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48v-41.6c0-74.2-60.2-134.4-134.4-134.4z"
          ></path>
        </svg>
      </div>
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
        class="origin-top-right z-10 absolute top-full min-w-36 bg-neutral-600 py-1.5 rounded shadow-lg overflow-hidden mt-1"
        :class="align === 'right' ? 'right-0' : 'left-0'"
      >
        <ul
          ref="dropdown"
          @focusin="dropdownOpen = true"
          @focusout="dropdownOpen = false"
        >
          <li>
            <router-link
              class="font-medium text-sm text-white hover:text-neutral-300 w-full flex items-center justify-center py-1 px-3"
              to="/demo/mypage"
              @click="dropdownOpen = false"
              >マイページ</router-link
            >
          </li>
          <li>
            <button
              class="font-medium text-sm text-white hover:text-neutral-300 w-full flex items-center justify-center py-1 px-3"
              @click="confirmLogout"
            >
              ログアウト
            </button>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import UserAvatar from '../images/user-avatar-32.png';

export default {
  name: 'DropdownProfile',
  props: ['align'],
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
    };
  },
  // ログアウトの確認ダイアログ
  methods: {
    confirmLogout() {
      const result = confirm('ログアウトしますか？');
      if (!result) {
        return;
      }
      this.logOut();
    },
    // ログアウト処理
    logOut() {
      this.$router.push({ name: 'Signin' });
      alert('ログアウトしました');
    },
  },
  data() {
    return {
      UserAvatar: UserAvatar,
    };
  },
};
</script>
