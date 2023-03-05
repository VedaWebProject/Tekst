import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router';
import { useAuthStore, useMessagesStore } from '@/stores';
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
import { usePlatformStore } from '@/stores';

declare module 'vue-router' {
  interface RouteMeta {
    title: string;
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
      meta: {
        title: 'Home',
      },
    },
    {
      path: '/browse/:text?',
      name: 'browse',
      component: BrowseView,
      meta: {
        title: 'Browse',
      },
    },
    {
      path: '/search/:text?',
      name: 'search',
      component: SearchView,
      meta: {
        title: 'Search',
      },
    },
    {
      path: '/help',
      name: 'help',
      component: HelpView,
      meta: {
        title: 'Help',
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        title: 'Login',
      },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: {
        title: 'Register',
      },
    },
    {
      path: '/account',
      name: 'account',
      component: AccountView,
      meta: {
        title: 'Account',
        restricted: 'user',
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: {
        title: 'Admin',
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

export function setPageTitle(route: RouteLocationNormalized) {
  const pf = usePlatformStore();
  const pfName = pf.data?.info?.platformName;
  const routeTitle = route.meta?.title;
  const divider = pfName && routeTitle ? ' - ' : '';
  document.title = `${pfName}${divider}${routeTitle || ''}`;
}

router.beforeEach((to) => {
  return applyRouteRestrictions(to);
});

router.afterEach((to) => {
  setPageTitle(to);
});

export default router;
