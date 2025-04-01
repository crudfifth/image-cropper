import { createRouter, createWebHistory } from 'vue-router';

import SetPassword from '@/pages/SetPassword.vue';
import SetUserInfo from '@/pages/SetUserInfo.vue';

import RequestResetPassword from './pages/RequestResetPassword.vue';
import ResetPassword from './pages/ResetPassword.vue';
import ChangePassword from './pages/ChangePassword.vue';
import SignIn from './pages/SignIn.vue';
import SignupContainer from './pages/SignupContainer.vue';
import VerifyEmail from './pages/VerifyEmail.vue';

import AuthTokenRepository from './repositories/AuthTokenRepository';

// 新しいコンポーネントディレクトリからのインポート
import SignUpWithMagicLink from '@components/pages/SignUpWithMagicLink/SignUpWithMagicLink.vue';
import SignInNew from '@components/pages/SignIn/SignIn.vue';
import RequestResetPasswordNew from '@components/pages/RequestResetPassword/RequestResetPassword.vue';
import ResetPasswordNew from '@components/pages/ResetPassword/ResetPassword.vue';
import TrendGraph from '@components/pages/TrendGraph/TrendGraph.vue';
import CarbonFootprint from '@components/pages/CarbonFootprint/CarbonFootprint.vue';
import DisplaySettings from '@components/pages/DisplaySettings/DisplaySettings.vue';
import MyPage from '@components/pages/MyPage/MyPage.vue';
import MyPageEdit from '@components/pages/MyPageEdit/MyPageEdit.vue';
import GatewaySettings from '@components/pages/GatewaySettings/GatewaySettings.vue';
import UserSettings from '@components/pages/UserSettings/UserSettings.vue';
import OperationCSVUpload from '@components/pages/OperationCSVUpload/OperationCSVUpload.vue';

const routerHistory = createWebHistory();

const router = createRouter({
  history: routerHistory,
  routes: [
    {
      path: '/signup-with-magic-link',
      component: SignUpWithMagicLink,
      name: 'signup-with-magic-link',
    },
    {
      path: '/signin',
      component: SignInNew,
      name: 'SignIn',
    },
    {
      path: '/gateway-settings',
      component: GatewaySettings,
      name: 'gateway-settings',
      meta: { requiresAuth: true },
    },
    {
      path: '/',
      component: TrendGraph,
      name: 'trend-graph',
      meta: { requiresAuth: true },
    },
    {
      path: '/display-settings',
      component: DisplaySettings,
      name: 'display-settings',
      meta: { requiresAuth: true },
    },
    {
      path: '/carbon-footprint',
      component: CarbonFootprint,
      name: 'carbon-footprint',
      meta: { requiresAuth: true },
    },
    {
      path: '/user-settings',
      component: UserSettings,
      name: 'user-settings',
      meta: { requiresAuth: true },
    },
    {
      path: '/csv-upload',
      component: OperationCSVUpload,
      name: 'csv-upload',
      meta: { requiresAuth: true },
    },
    {
      path: '/mypage',
      component: MyPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/mypage-edit',
      component: MyPageEdit,
      meta: { requiresAuth: true },
    },
    {
      path: '/signin-old',
      component: SignIn,
      name: 'SignInOld',
    },
    {
      path: '/signup',
      component: SignupContainer,
    },
    {
      path: '/set-password',
      component: SetPassword,
      name: 'setPassword',
    },
    {
      path: '/change-password',
      component: ChangePassword,
      name: 'changePassword',
      meta: { requiresAuth: true },
    },
    {
      path: '/set-user-info',
      component: SetUserInfo,
      name: 'setUserInfo',
    },
    {
      path: '/verify-email/:token',
      component: VerifyEmail,
    },
    {
      path: '/request-reset-password-old',
      component: RequestResetPassword,
    },
    {
      path: '/reset-password',
      component: ResetPasswordNew,
    },
    {
      path: '/request-reset-password',
      component: RequestResetPasswordNew,
    },
    // {
    //   path: '/:pathMatch(.*)*',
    //   component: PageNotFound,
    // },
  ],
});

// 画面遷移前にログイン済みかをチェックして、未ログイン時はログイン画面に強制遷移させる
router.beforeEach(async (to, from, next) => {
  // ログインチェック
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    const token = AuthTokenRepository.getToken();
    if (token) {
      next();
      return;
    }
    next({ path: '/signin' });
    return;
  }
  next();
});

export default router;
