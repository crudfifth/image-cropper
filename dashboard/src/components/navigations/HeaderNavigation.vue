<!-- TODO: Composition APIを使ってリファクタリングする -->
<template>
  <header class="sticky top-0 bg-white shadow-lg z-30">
    <div class="px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 -mb-px">
        <!-- Header: Left side -->
        <div class="flex">
          <!-- Hamburger button -->
          <button
            class="text-gray-500 hover:text-gray-600 lg:hidden"
            aria-controls="sidebar"
            :aria-expanded="sidebarOpen"
            @click.stop="$emit('toggle-sidebar')"
          >
            <span class="sr-only">Open sidebar</span>
            <svg
              class="w-6 h-6 fill-current"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect x="4" y="5" width="16" height="2" />
              <rect x="4" y="11" width="16" height="2" />
              <rect x="4" y="17" width="16" height="2" />
            </svg>
          </button>
        </div>

        <div class="flex-1">
          <p class="text-sm">
            本日は、<span class="text-base font-bold">{{
              nenGaPpi(date)
            }}</span>
          </p>
        </div>

        <!-- Header: Right side -->
        <div class="flex items-center space-x-3">
          <!-- <select
            v-model="selectedCompanyId"
            class="form-select disabled:bg-slate-50 disabled:border-slate-200 disabled:shadow-none"
            @change="onChange"
          >
            <option
              v-for="c in companies"
              :key="c.id"
              :value="c.id"
              :selected="selectedCompanyId === c.id"
            >
              {{ c.name }}
            </option>
          </select> -->

          <div class="relative inline-block text-left">
            <div>
              <button
                @click="toggleDropdown"
                type="button"
                class="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-indigo-500"
                id="menu-button"
                aria-expanded="true"
                aria-haspopup="true"
              >
                Language: {{ selectedLanguage }}
                <svg
                  class="-mr-1 ml-2 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
              <div
                v-if="dropdownOpen"
                class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
                role="menu"
                aria-orientation="vertical"
                aria-labelledby="menu-button"
                tabindex="-1"
              >
                <div class="py-1" role="none">
                  <!-- Active: "bg-gray-100 text-gray-900", Not Active: "text-gray-700" -->
                  <a
                    @click="selectLanguage('日本語')"
                    href="#"
                    class="text-gray-700 block px-4 py-2 text-sm"
                    role="menuitem"
                    tabindex="-1"
                    id="menu-item-0"
                    >日本語</a
                  >
                  <a
                    @click="selectLanguage('English')"
                    href="#"
                    class="text-gray-700 block px-4 py-2 text-sm"
                    role="menuitem"
                    tabindex="-1"
                    id="menu-item-1"
                    >English</a
                  >
                </div>
              </div>
            </div>
          </div>

          <p class="pr-3">ユーザー名：{{ userName }}</p>
          <UserMenu align="right" :account="account" />
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { onMounted, ref } from 'vue';

import UserRepository from '@/repositories/UserRepository';
import CompanyService from '@/services/CompanyService';
import moment from 'moment';
import 'moment/dist/locale/ja';
//import Help from '@/components/DropdownHelp.vue';
import UserMenu from '@/components/DropdownProfile.vue';
//import SearchModal from '@/components/ModalSearch.vue';
import NotificationService from '@/services/NotificationService';
import UserService from '@/services/UserService';

export default {
  name: 'HeaderNavigation',
  components: {
    //SearchModal,
    //DropdownNotifications,
    UserMenu,
    //Help,
    //UserMenu,
  },
  props: ['sidebarOpen'],
  setup() {
    const searchModalOpen = ref(false);
    const userId = ref('');
    const userName = ref('');
    const notifications = ref([]);
    const companies = ref([]);
    const selectedCompanyId = ref('');
    const selectedLanguage = ref('日本語'); // 初期言語を日本語に設定
    const languages = ref({ ja: '日本語' }); // 言語の選択肢

    onMounted(async () => {
      const user = await UserService.fetchCurrentUser().catch(() => {
        return;
      });
      userId.value = user.id;
      userName.value = user.username;

      const notificationPageItem =
        await NotificationService.fetchNotifications().catch(() => {
          return;
        });
      notifications.value = notificationPageItem.results?.slice(0, 3);
    });

    const onChange = (e) => {
      UserRepository.setSelectedCompany(e.target.value);
      location.reload();
    };

    return {
      searchModalOpen,
      userId,
      userName,
      notifications,
      companies,
      onChange,
      selectedLanguage,
      languages,
    };
  },
  methods: {
    nenGaPpi(date) {
      moment.locale('ja');
      return moment(date).format('YYYY年M月D日 (dd)');
    },
  },
};
</script>
