<template>
  <div class="h-full bg-white shadow-lg rounded-md py-8 px-10">
    <div class="flex justify-between items-center">
      <div class="ml-4 mb-2">
        <div class="flex items-center mb-4">
          <ListIcon class="mr-2" />
          <div class="text-2xl font-bold">ユーザー一覧</div>
        </div>
        <div class="font-bold text-xl">会社名：{{ company?.name }}</div>
      </div>
      <div class="flex items-center mb-2 mr-8">
        <button
          v-if="adding || checkedUserId !== undefined"
          class="mr-2 flex items-center justify-center px-4 rounded bg-white border-2 border-solid-black hover:bg-slate-100 text-slate-500 py-2 font-bold"
          @click="cancelAdd"
        >
          キャンセル
        </button>
        <AddButton
          class="mr-2"
          :on-click-async="onClickAdd"
          :disabled="adding || checkedUserId !== undefined || !validAddingUser"
        />
        <SubmitButton
          class="mr-2"
          :is-adding="adding"
          :on-click-async="updateUser"
          :disabled="!adding && checkedUserId === undefined"
        />
        <DeleteButton
          class="mr-2"
          :on-click-async="deleteUser"
          :disabled="disableDeleteButton"
        />
      </div>
    </div>
    <div class="flex flex-col mb-4 overflow-auto whitespace-nowrap">
      <table class="border-separate border-spacing-x-4">
        <thead class="text-center text-sm sticky top-0 bg-white z-10">
          <tr>
            <th rowspan="2">チェック</th>
            <th class="border-b-2 border-gray-300 p-6" rowspan="2">部署名</th>
            <th class="border-b-2 border-gray-300" rowspan="2">担当者名</th>
            <th class="border-b-2 border-gray-300" rowspan="2">ログインID</th>
            <th class="border-b-2 border-gray-300" colspan="2">権限</th>
            <th class="border-b-2 border-gray-300" rowspan="2">ロック</th>
          </tr>
          <tr>
            <th class="border-b-2 border-gray-300">設定</th>
            <th class="border-b-2 border-gray-300">閲覧</th>
          </tr>
        </thead>
        <tbody class="font-medium">
          <tr v-if="adding" class="h-[60px]">
            <td class="text-center">新規追加</td>
            <td class="border-b-2 boder-gray-200 p-4 text-center">
              <input
                v-model="addingUser.affiliation"
                class="form-input"
                :class="{
                  'border-2 border-red-500': !validateField(
                    addingUser,
                    'affiliation'
                  ),
                }"
                type="text"
              />
            </td>
            <td class="border-b-2 boder-gray-200 text-center">
              <input
                v-model="addingUser.username"
                class="form-input"
                :class="{
                  'border-2 border-red-500': !validateField(
                    addingUser,
                    'username'
                  ),
                }"
                type="text"
              />
            </td>
            <td class="border-b-2 boder-gray-200 text-center">
              <input
                v-model="addingUser.email"
                class="form-input"
                :class="{
                  'border-2 border-red-500': !validateField(
                    addingUser,
                    'email'
                  ),
                }"
                type="email"
              />
            </td>
            <td class="border-b-2 boder-gray-200 text-center"></td>
            <td class="border-b-2 boder-gray-200 text-center"></td>
            <td class="border-b-2 boder-gray-200 text-center"></td>
          </tr>
          <tr
            v-for="user in userList"
            :key="user.id"
            class="h-[60px] text-center font-medium text-md"
          >
            <td>
              <input
                class="form-checkbox"
                :class="{ 'bg-gray-200': adding, 'opacity-70': adding }"
                type="checkbox"
                :checked="checkedUserId === user.id"
                :disabled="adding"
                @change="onChangeCheck($event, user)"
              />
            </td>
            <td class="border-b-2 boder-gray-200 p-4">
              <span v-if="checkedUserId !== user.id">{{
                user.affiliation
              }}</span>
              <input
                v-else
                v-model="user.affiliation"
                class="form-input"
                :class="{
                  'border-2 border-red-500': !validateField(
                    user,
                    'affiliation'
                  ),
                }"
                type="text"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <span v-if="checkedUserId !== user.id">{{ user.username }}</span>
              <input
                v-else
                v-model="user.username"
                class="form-input"
                :class="{
                  'border-2 border-red-500': !validateField(user, 'username'),
                }"
                type="text"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <span>{{ user.email }}</span>
            </td>
            <td class="border-b-2 boder-gray-200">
              <input
                v-if="user.is_manager"
                checked
                disabled
                class="form-checkbox bg-slate-200 text-slate-400"
                type="checkbox"
              />
              <input
                v-else-if="checkedUserId !== user.id"
                v-model="user.has_manage_role"
                class="form-checkbox bg-slate-200 text-slate-400"
                type="checkbox"
                disabled
              />
              <input
                v-else
                v-model="user.has_manage_role"
                class="form-checkbox"
                :class="{
                  'bg-slate-200': !hasManageAuthority,
                }"
                type="checkbox"
                :disabled="!hasManageAuthority"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <input
                v-if="user.is_manager"
                checked
                disabled
                class="form-checkbox bg-slate-200 text-slate-400"
                type="checkbox"
              />
              <input
                v-else-if="checkedUserId !== user.id"
                v-model="user.has_view_role"
                class="form-checkbox bg-slate-200 text-slate-400"
                type="checkbox"
                disabled
              />
              <input
                v-else
                v-model="user.has_view_role"
                class="form-checkbox"
                :class="{
                  'bg-slate-200 text-slate-400': !hasManageAuthority,
                }"
                type="checkbox"
                :disabled="!hasManageAuthority"
              />
            </td>
            <td class="border-b-2 boder-gray-200">
              <input
                v-model="user.is_locked"
                class="form-checkbox bg-slate-200 text-slate-400"
                type="checkbox"
                disabled
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import ListIcon from '@icons/ListIcon.vue';
import AddButton from '../presenters/AddButton.vue';
import SubmitButton from '../presenters/SubmitButton.vue';
import DeleteButton from '../presenters/DeleteButton.vue';
import CompanyService from '@/services/CompanyService';
import { Company } from '@/types';
import { User } from '@/repositories/UserRepository';
import UserService from '@/services/UserService';
import { cloneDeep } from 'lodash-es';
import { UserConflictError } from '@/services/UserService';
import { AxiosError } from 'axios';
import { z } from 'zod';
import { openConfirmModal } from '@/stores/ConfirmModalStore';
import { openAlertModal } from '@/stores/AlertModalStore';
import { userCountStore } from '@/stores/UserSettingsStore';
import { userInfoStore } from '@/stores/HeaderNavigationStore';

const company = ref<Company | undefined>(undefined);
const initialUserList = ref<User[]>([]);

type UserFormData = Pick<
  User,
  'username' | 'email' | 'affiliation' | 'is_locked' | 'company_id'
>;

const userList = ref<User[]>([]);
const currentUser = ref<User | undefined>(undefined);
onMounted(async () => {
  company.value = await CompanyService.fetchSelectedCompany();
  userList.value = await UserService.fetchUsers();
  currentUser.value = await UserService.fetchCurrentUser();
  // initialUserList.value = cloneDeep(userList.value);
});

const checkedUserId = ref<string | undefined>(undefined);

const onChangeCheck = (e: Event, user: User) => {
  checkedUserId.value = (e.target as HTMLInputElement).checked
    ? user.id
    : undefined;
};

const updateUser = async () => {
  if (adding.value && company.value) {
    addingUser.value.company_id = company.value.id;
    try {
      const createdUser = await UserService.signup(addingUser.value);
      userList.value.unshift(createdUser);
      userCountStore.userCount += 1;

      openAlertModal({
        body: '新規追加されたユーザに対し、会員登録のURLを送付しました。有効期間は30分となります。会員登録をするよう連絡をお願いします。',
      });
    } catch (e) {
      if (e instanceof UserConflictError) {
        openAlertModal({ body: e.message });
      }
      return;
    }
  }
  const user = userList.value.find((u) => u.id === checkedUserId.value);
  if (user) {
    try {
      await UserService.update(user.id, user);
      if (user.id === userInfoStore.userId) {
        userInfoStore.userName = user.username;
      }
    } catch (e) {
      const err = e as AxiosError;
      openAlertModal({
        body: (err.response?.data as { message: string }).message,
      });
      return;
    }
  }
  adding.value = false;
  addingUser.value = {
    username: '',
    email: '',
    affiliation: '',
    is_locked: false,
    company_id: company.value?.id,
  };
  checkedUserId.value = undefined;
};

const deleteUser = async () => {
  openConfirmModal({
    body: '削除しますか？',
    onResponse: async (confirmed: boolean) => {
      if (confirmed && checkedUserId.value) {
        await UserService.deleteUser(checkedUserId.value);
        const targetUser = userList.value.find(
          (u) => u.id === checkedUserId.value
        );
        if (targetUser?.is_active && !targetUser.is_locked) {
          userCountStore.activeUserCount -= 1;
        }
        userCountStore.userCount -= 1;
        userList.value = userList.value.filter(
          (u) => u.id !== checkedUserId.value
        );
        checkedUserId.value = undefined;
      }
    },
  });
};

const adding = ref(false);
const addingUser = ref<UserFormData>({
  username: '',
  email: '',
  affiliation: '',
  is_locked: false,
  company_id: company.value?.id,
});

const onClickAdd = async () => {
  if (userCountStore.userLimit <= userCountStore.userCount) {
    openAlertModal({
      body: 'ユーザー登録上限数に達しています',
    });
    return;
  }
  adding.value = true;
};

const emailSchema = z.string().min(1).email();
const stringSchema = z.string().min(1);
const validateField = (
  user: Omit<UserFormData, 'is_locked'>,
  field: keyof Omit<UserFormData, 'is_locked'>
) => {
  if (field === 'email') {
    return emailSchema.safeParse(user[field]).success;
  }
  return stringSchema.safeParse(user[field]).success;
};

const validAddingUser = computed(() => {
  if (!adding.value) {
    return true;
  }
  return (
    validateField(addingUser.value, 'username') &&
    validateField(addingUser.value, 'email') &&
    validateField(addingUser.value, 'affiliation')
  );
});

const validEditingUser = computed(() => {
  const user = userList.value.find((u) => u.id === checkedUserId.value);
  if (user) {
    return (
      validateField(user, 'username') &&
      validateField(user, 'email') &&
      validateField(user, 'affiliation')
    );
  }
  return false;
});

const cancelAdd = () => {
  adding.value = false;
  addingUser.value = {
    username: '',
    email: '',
    affiliation: '',
    is_locked: false,
    company_id: company.value?.id,
  };
  checkedUserId.value = undefined;
};

const disableDeleteButton = computed(
  () =>
    checkedUserId.value === undefined ||
    userList.value.find((u) => u.id === checkedUserId.value)?.is_manager
);

const hasManageAuthority = computed(() => {
  return currentUser.value?.is_manager || currentUser.value?.has_manage_role;
});
</script>
