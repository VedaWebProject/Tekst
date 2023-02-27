import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router';
import { useAuthStore, useMessagesStore } from '@/stores';
import {
  AboutView,
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

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'about',
      component: AboutView,
      meta: {
        title: 'About',
      },
    },
    {
      path: '/home',
      redirect: '/',
    },
    {
      path: '/browse',
      name: 'browse',
      component: BrowseView,
      meta: {
        title: 'Browse',
      },
    },
    {
      path: '/search',
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
    const t = i18n.global.t;
    const auth = useAuthStore();
    const messages = useMessagesStore();
    const ru = route.meta.restricted === 'user'; // route is restricted to users
    const rsu = route.meta.restricted === 'superuser'; // route is restricted to to superusers
    const l = auth.loggedIn; // a user is logged in
    const u = auth.user?.isActive && auth.user?.isVerified; // the user is a verified, active user
    const su = auth.user?.isSuperuser; // the user is a superuser
    const authorized = (ru && l && u) || (rsu && l && su);
    // redirect if trying to access a restricted page without aithorization
    if (!authorized) {
      auth.returnUrl = route.fullPath;
      messages.warning(t('errors.noAccess', { resource: route.path }));
      return '/home';
    }
  }
}

export function setPageTitle(route: RouteLocationNormalized) {
  const pf = usePlatformStore();
  const pfName = pf.get('info.platformName');
  const routeTitle = route.meta?.title;
  const divider = pfName && routeTitle ? ' - ' : '';
  document.title = `${pfName}${divider}${routeTitle}`;
}

router.beforeEach(async (to) => {
  return applyRouteRestrictions(to);
});

router.afterEach((to) => {
  setPageTitle(to);
});

export default router;
