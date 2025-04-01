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
            本日は、
            <span class="text-base font-bold">{{ nenGaPpi(date) }}</span>
            です。今日も一日頑張りましょう。
          </p>
        </div>

        <!-- Header: Right side -->
        <div class="flex items-center space-x-3">
          <LanguageSelector />

          <button
            id="print-as-pdf"
            class="flex items-center gap-1 text-sm bg-white hover:bg-blue-500 hover:text-white py-2 px-4 border-2 hover:border-transparent rounded"
            @click="setOutput('pdf')"
          >
            <PdfIcon color="text-main-blue" class="w-6 h-6 inline" />
            pdfで出力する
          </button>

          <button
            id="print"
            class="flex items-center gap-1 text-sm bg-white hover:bg-blue-500 hover:text-white py-2 px-4 border-2 hover:border-transparent rounded"
            @click="setOutput('print')"
          >
            <PrinterIcon color="text-main-blue" class="w-6 h-6 inline" />
            印刷する
          </button>

          <p class="pr-3">ユーザー名：{{ userName }}</p>
          <UserMenu align="right" :account="account" />
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { onMounted, ref, watchEffect } from 'vue';

import UserRepository from '@/repositories/UserRepository';
import CompanyService from '@/services/CompanyService';
import moment from 'moment';
import 'moment/dist/locale/ja';
//import Help from '@/components/DropdownHelp.vue';
import UserMenu from './UserMenu.vue';
//import SearchModal from '@/components/ModalSearch.vue';
import UserService from '@/services/UserService';
import { userInfoStore } from '@/stores/HeaderNavigationStore';
import LanguageSelector from '../presenters/composites/LanguageSelector.vue';
import * as htmlToImage from 'html-to-image';
import jsPDF from 'jspdf';
import PdfIcon from '@icons/PdfIcon.vue';
import PrinterIcon from '@icons/PrinterIcon.vue';

export default {
  name: 'HeaderNavigation',
  components: {
    //SearchModal,
    //DropdownNotifications,
    UserMenu,
    LanguageSelector,
    PdfIcon,
    PrinterIcon,
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
    const selectedLanguage = ref('日本語'); // 初期言語を日本語に設定
    const languages = ref({ ja: '日本語' }); // 言語の選択肢

    onMounted(async () => {
      const user = await UserService.fetchCurrentUser().catch(() => {
        return;
      });
      userInfoStore.userId = user.id;
      userInfoStore.userName = user.username;
    });

    const onChange = (e) => {
      UserRepository.setSelectedCompany(e.target.value);
      location.reload();
    };

    watchEffect(() => {
      userId.value = userInfoStore.userId;
      userName.value = userInfoStore.userName;
    });

    const setOutput = async (action) => {
      let node = document.getElementById('drawing');
      const dataUrl = await htmlToImage.toPng(node);

      const doc = new jsPDF({
        orientation: 'landscape',
        format: 'a4',
      });
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();

      let img = new Image();
      const PADDING = 20;
      img.onload = function () {
        let imgWidth = pageWidth - PADDING;
        let imgHeight = (img.height * imgWidth) / img.width;

        if (imgHeight > pageHeight) {
          imgHeight = pageHeight - PADDING;
          imgWidth = (img.width * imgHeight) / img.height;
        }

        doc.addImage(dataUrl, 'PNG', 10, 10, imgWidth, imgHeight);

        switch (action) {
          case 'pdf':
            doc.save('output.pdf');
            break;

          case 'print':
            var w = window.open(doc.output('bloburl'), '_blank');
            w.onload = function () {
              w.print();
            };
            break;
        }
      };
      img.src = dataUrl;
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
      setOutput,
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
