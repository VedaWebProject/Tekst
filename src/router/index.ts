import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router';
import { useAuthStore, useMessagesStore, useStateStore } from '@/stores';
import {
  HomeView,
  AccountView,
  LoginView,
  RegisterView,
  HelpView,
  BrowseView,
  SearchView,
  AdminView,
} from '@/views';
import { i18n } from '@/i18n';

declare module 'vue-router' {
  interface RouteMeta {
    restricted?: 'user' | 'superuser';
  }
}

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
    },
    {
      path: '/search/:text?',
      name: 'search',
      component: SearchView,
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
      path: '/account',
      name: 'account',
      component: AccountView,
      meta: {
        restricted: 'user',
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: {
        restricted: 'superuser',
      },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

function applyRouteRestrictions(route: RouteLocationNormalized) {
  // enforce route restrictions
  if (route.meta?.restricted) {
    const auth = useAuthStore();
    const ru = route.meta.restricted === 'user'; // route is restricted to users
    const rsu = route.meta.restricted === 'superuser'; // route is restricted to to superusers
    const l = auth.loggedIn; // a user is logged in
    const u = auth.user?.isActive && auth.user?.isVerified; // the user is a verified, active user
    const su = auth.user?.isSuperuser; // the user is a superuser
    const authorized = (ru && l && u) || (rsu && l && su);
    // redirect if trying to access a restricted page without aithorization
    if (!authorized) {
      auth.returnUrl = route.fullPath;
      const messages = useMessagesStore();
      messages.warning(i18n.global.t('errors.noAccess', { resource: route.path }));
      return { name: 'login' };
    }
  }
}

router.beforeEach((to) => {
  return applyRouteRestrictions(to);
});

router.afterEach((to) => {
  useStateStore().setPageTitle(to);
});

export default router;
