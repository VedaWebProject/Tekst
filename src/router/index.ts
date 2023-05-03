import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore, useStateStore } from '@/stores';
import { i18n } from '@/i18n';
import { useMessages } from '@/messages';
import { usePlatformData } from '@/platformData';

declare module 'vue-router' {
  interface RouteMeta {
    restricted?: 'user' | 'superuser';
    isTextSpecific?: boolean;
  }
}

const HomeView = () => import('@/views/HomeView.vue');
const UserView = () => import('@/views/UserView.vue');
const AccountView = () => import('@/views/account/AccountView.vue');
const AccountManageView = () => import('@/views/account/AccountManageView.vue');
const HelpView = () => import('@/views/HelpView.vue');
const BrowseView = () => import('@/views/BrowseView.vue');
const SearchView = () => import('@/views/SearchView.vue');

const RegisterView = () => import('@/views/RegisterView.vue');

const AdminView = () => import('@/views/admin/AdminView.vue');
const AdminStatisticsView = () => import('@/views/admin/AdminStatisticsView.vue');
const AdminUsersView = () => import('@/views/admin/AdminUsersView.vue');

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
      path: '/user/:username',
      name: 'user',
      component: UserView,
    },
    {
      path: '/account',
      component: AccountView,
      meta: {
        restricted: 'user',
      },
      children: [
        {
          path: '',
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
      component: AdminView,
      meta: {
        restricted: 'superuser',
      },
      children: [
        {
          path: '',
          name: 'adminStatistics',
          component: AdminStatisticsView,
        },
        {
          path: 'users',
          name: 'adminUsers',
          component: AdminUsersView,
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

router.beforeEach(async (to, from, next) => {
  // check if route is disabled
  const { pfData } = usePlatformData();
  if (to.name === 'register' && !pfData.value?.security?.enableRegistration) {
    next({ name: 'home' });
  }
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
        auth.returnUrl = to.fullPath;
        next(from || { name: 'home' });
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
