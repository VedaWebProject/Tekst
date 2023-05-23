import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore, useStateStore } from '@/stores';
import { i18n } from '@/i18n';
import { useMessages } from '@/messages';

declare module 'vue-router' {
  interface RouteMeta {
    restricted?: 'user' | 'superuser';
    isTextSpecific?: boolean;
  }
}

const HomeView = () => import('@/views/HomeView.vue');
const UserView = () => import('@/views/UserView.vue');
const HelpView = () => import('@/views/HelpView.vue');
const BrowseView = () => import('@/views/BrowseView.vue');
const SearchView = () => import('@/views/SearchView.vue');
const LoginView = () => import('@/views/LoginView.vue');
const RegisterView = () => import('@/views/RegisterView.vue');

const AccountView = () => import('@/views/account/AccountView.vue');
const AccountManageView = () => import('@/views/account/AccountManageView.vue');
const VerifyView = () => import('@/views/VerifyView.vue');
const ResetView = () => import('@/views/ResetView.vue');

const AdminView = () => import('@/views/admin/AdminView.vue');
const AdminStatisticsView = () => import('@/views/admin/AdminStatisticsView.vue');
const AdminUsersView = () => import('@/views/admin/AdminUsersView.vue');
const AdminTextsView = () => import('@/views/admin/AdminTextsView.vue');
const AdminTextsGeneralView = () => import('@/views/admin/AdminTextsGeneralView.vue');
const AdminTextsStructureView = () => import('@/views/admin/AdminTextsStructureView.vue');
const AdminNewTextView = () => import('@/views/admin/AdminNewTextView.vue');

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/browse/:text?',
      name: 'browse',
      component: BrowseView,
      meta: {
        isTextSpecific: true,
      },
    },
    {
      path: '/search/:text?',
      name: 'search',
      component: SearchView,
      meta: {
        isTextSpecific: true,
      },
    },
    {
      path: '/help',
      name: 'help',
      component: HelpView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/user/:username',
      name: 'user',
      component: UserView,
    },
    {
      path: '/verify',
      name: 'verify',
      component: VerifyView,
    },
    {
      path: '/reset',
      name: 'reset',
      component: ResetView,
    },
    {
      path: '/account',
      component: AccountView,
      meta: {
        restricted: 'user',
      },
      children: [
        {
          path: 'profile',
          name: 'accountProfile',
          component: UserView,
        },
        {
          path: 'manage',
          name: 'accountManage',
          component: AccountManageView,
        },
      ],
    },
    {
      path: '/admin',
      name: 'admin',
      redirect: { name: 'adminStatistics' },
      component: AdminView,
      meta: {
        restricted: 'superuser',
      },
      children: [
        {
          path: 'statistics',
          name: 'adminStatistics',
          component: AdminStatisticsView,
        },
        {
          path: 'users',
          name: 'adminUsers',
          component: AdminUsersView,
        },
        {
          path: 'texts/:text',
          name: 'adminTexts',
          redirect: { name: 'adminTextsGeneral' },
          component: AdminTextsView,
          meta: {
            isTextSpecific: true,
          },
          children: [
            {
              path: 'general',
              name: 'adminTextsGeneral',
              component: AdminTextsGeneralView,
            },
            {
              path: 'structure',
              name: 'adminTextsStructure',
              component: AdminTextsStructureView,
            },
          ],
        },
        {
          path: 'new-text',
          name: 'adminNewText',
          component: AdminNewTextView,
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

router.beforeEach(async (to, from, next) => {
  // enforce route restrictions
  if (to.meta?.restricted) {
    const auth = useAuthStore();
    const ru = to.meta.restricted === 'user'; // route is restricted to users
    const rsu = to.meta.restricted === 'superuser'; // route is restricted to to superusers
    const l = auth.loggedIn; // a user is logged in
    const u = auth.user?.isActive && auth.user?.isVerified; // the user is a verified, active user
    const su = auth.user?.isSuperuser; // the user is a superuser
    const authorized = (ru && l && u) || (rsu && l && su);
    // redirect if trying to access a restricted page without authorization
    if (!authorized) {
      const { message } = useMessages();
      message.warning(i18n.global.t('errors.noAccess', { resource: to.path }));
      if (auth.loggedIn) {
        next({ name: 'home' });
      } else {
        next(from || { name: 'home' });
        auth.showLoginModal(i18n.global.t('errors.logInToAccess'), to.fullPath, false);
      }
      return; // this is important!
    }
  }
  // proceed to next hook in router pipeline
  next();
});

router.afterEach((to) => {
  useStateStore().setPageTitle(to);
});

export default router;
