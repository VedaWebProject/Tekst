import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore, useMessagesStore, useStateStore } from '@/stores';
import { i18n } from '@/i18n';

declare module 'vue-router' {
  interface RouteMeta {
    restricted?: 'user' | 'superuser';
    isTextSpecific?: boolean;
  }
}

const HomeView = () => import('@/views/HomeView.vue');
const UserView = () => import('@/views/UserView.vue');
const AccountView = () => import('@/views/AccountView.vue');
const LoginView = () => import('@/views/LoginView.vue');
const RegisterView = () => import('@/views/RegisterView.vue');
const HelpView = () => import('@/views/HelpView.vue');
const BrowseView = () => import('@/views/BrowseView.vue');
const SearchView = () => import('@/views/SearchView.vue');
const UsersView = () => import('@/views/UsersView.vue');

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
      path: '/login',
      name: 'login',
      component: LoginView,
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
      name: 'account',
      component: AccountView,
      meta: {
        restricted: 'user',
      },
    },
    {
      path: '/users',
      name: 'users',
      component: UsersView,
      meta: {
        restricted: 'superuser',
      },
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
    // redirect if trying to access a restricted page without aithorization
    if (!authorized) {
      auth.returnUrl = to.fullPath;
      const messages = useMessagesStore();
      messages.warning(i18n.global.t('errors.noAccess', { resource: to.path }));
      next({ name: 'login' });
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
