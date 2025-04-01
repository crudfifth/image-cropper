<!-- TODO: partials/Sidebar.vueからコピー。古い方をあとで消す -->
<template>
  <div class="shadow-lg z-50">
    <!-- Sidebar backdrop (mobile only) -->
    <div
      class="fixed inset-0 z-40 lg:hidden lg:z-auto transition-opacity duration-200"
      :class="sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'"
      aria-hidden="true"
    ></div>

    <!-- Sidebar -->
    <div
      id="sidebar"
      ref="sidebar"
      class="flex flex-col absolute z-40 left-0 top-0 lg:static left-auto top-auto translate-x-0 h-screen overflow-y-scroll overflow-y-auto no-scrollbar w-20 sidebar-expanded:!w-[300px] shrink-0 bg-white p-4 transition-all duration-200 ease-in-out"
    >
      <!-- Sidebar header -->
      <div class="flex justify-center mb-5 px-2">
        <!-- Logo -->
        <router-link class="block" :to="{ path: `/`, query: $route.query }">
          <img
            v-if="sidebarExpanded"
            src="@/images/logo.png"
            alt="Logo"
            class="h-[72px]"
          />
          <img v-else src="@/images/logo_min.png" alt="Logo" />
        </router-link>
      </div>

      <!-- Links -->
      <div class="space-y-8 h-3/4 rounded-md">
        <!-- Pages group -->
        <div class="p-2">
          <ul class="">
            <NavigationEntry
              path="/"
              label="トレンドグラフ"
              :icon-component="GraphIcon"
              :is-expanded="sidebarExpanded"
            />

            <NavigationEntry
              path="/carbon-footprint"
              label="カーボンフットプリント"
              :icon-component="CarbonFootprintIcon"
              :is-expanded="sidebarExpanded"
            />

            <NavigationEntry
              path="/display-settings"
              label="表示設定"
              :icon-component="SettingsIcon"
              :is-expanded="sidebarExpanded"
            />

            <hr :class="{ sidebarExpanded: 'mx-2' }" />

            <NavigationEntry
              path="/gateway-settings"
              label="ゲートウェイ設定"
              :icon-component="GatewayIcon"
              :is-expanded="sidebarExpanded"
            />
            <NavigationEntry
              path="/user-settings"
              label="ユーザー設定"
              :icon-component="UserIcon"
              :is-expanded="sidebarExpanded"
            />
            <ExternalLinkEntry
              url="https://ihi-green-pf.com/contact.php"
              label="お問い合わせ"
              :icon-component="HomeIcon"
              :is-expanded="sidebarExpanded"
            />
          </ul>
        </div>
      </div>
      <!-- Expand / collapse button -->
      <div
        class="pt-3 hidden lg:inline-flex 2xl:inline-flex justify-end mt-auto"
      >
        <div class="px-3 py-2">
          <button @click.prevent="sidebarExpanded = !sidebarExpanded">
            <span class="sr-only">Expand / collapse sidebar</span>
            <svg
              class="w-6 h-6 fill-current sidebar-expanded:rotate-180"
              viewBox="0 0 24 24"
            >
              <path
                class="text-slate-400"
                d="M19.586 11l-5-5L16 4.586 23.414 12 16 19.414 14.586 18l5-5H7v-2z"
              />
              <path class="text-slate-600" d="M3 23H1V1h2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import GraphIcon from '@/components/icons/GraphIcon.vue';
import SettingsIcon from '@/components/icons/SettingsIcon.vue';
import CarbonFootprintIcon from '@/components/icons/CarbonFootprintIcon.vue';
import GatewayIcon from '@/components/icons/GatewayIcon.vue';
import NavigationEntry from '@/components/navigations/SideNavigation/NavigationEntry.vue';
import type { User } from '@/repositories/UserRepository';
import UserIcon from '@/components/icons/UserIcon.vue';
import ExternalLinkEntry from '@/components-new/common/presenters/composites/SideNavigationExternalLink.vue';
import HomeIcon from '@/components-new/common/presenters/icons/HomeIcon.vue';

const props = defineProps({
  sidebarOpen: Boolean,
});

const emit = defineEmits(['close-sidebar']);

const router = useRouter();
const route = useRoute();
const trigger = ref<HTMLButtonElement | null>(null);
const sidebar = ref<HTMLDivElement | null>(null);

const storedSidebarExpanded = localStorage.getItem('sidebar-expanded');
const sidebarExpanded = ref(
  storedSidebarExpanded === null ? false : storedSidebarExpanded === 'true'
);

// close on click outside
const clickHandler = ({ target }: { target: EventTarget | null }) => {
  if (!sidebar.value || !trigger.value) {
    return;
  }
  const targetNode = target as Node | null;
  if (
    !props.sidebarOpen ||
    sidebar.value.contains(targetNode) ||
    trigger.value.contains(targetNode)
  )
    return;
  emit('close-sidebar');
};

// close if the esc key is pressed
const keyHandler = ({ keyCode }: { keyCode: number }) => {
  if (!props.sidebarOpen || keyCode !== 27) return;
  emit('close-sidebar');
};

const handleResize = () => {
  if (window.innerWidth < 1024) {
    sidebarExpanded.value = false;
  }
};

const user = ref<User | undefined>(undefined);
//const isCompanyAdmin = ref(false);
onMounted(async () => {
  // try {
  //   user.value = await UserService.fetchCurrentUser();
  //   const selectedCompanyId = await UserService.getSelectedCompanyId();
  //   if (selectedCompanyId) {
  //     isCompanyAdmin.value = await CompanyService.fetchIsCompanyAdmin(
  //       selectedCompanyId
  //     );
  //   }
  //   if (!isCompanyAdmin.value && route.meta.adminPage) {
  //     router.push({ name: 'dashboard' });
  //   }
  // } catch {
  //   return;
  // }

  document.addEventListener('click', clickHandler);
  document.addEventListener('keydown', keyHandler);
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  document.removeEventListener('click', clickHandler);
  document.removeEventListener('keydown', keyHandler);
  window.removeEventListener('resize', handleResize);
});

watch(sidebarExpanded, () => {
  localStorage.setItem('sidebar-expanded', sidebarExpanded.value.toString());
  if (sidebarExpanded.value) {
    document.querySelector('body')?.classList.add('sidebar-expanded');
  } else {
    document.querySelector('body')?.classList.remove('sidebar-expanded');
  }
});
</script>
