import { GET } from '@/api';
import { useMessages } from '@/composables/messages';
import env from '@/env';
import { $t } from '@/i18n';
import { InfoIcon, PrivacyIcon, SiteNoticeIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { delay } from '@/utils';
import {
  createRouter,
  createWebHistory,
  type LocationQuery,
  type RouteLocationNamedRaw,
} from 'vue-router';

declare module 'vue-router' {
  interface RouteMeta {
    restricted?: 'user' | 'superuser';
  }
}

const UserView = () => import('@/views/UserView.vue');
const BrowseView = () => import('@/views/BrowseView.vue');
const SearchView = () => import('@/views/SearchView.vue');
const SearchResultsView = () => import('@/views/SearchResultsView.vue');
const LoginView = () => import('@/views/LoginView.vue');
const RegisterView = () => import('@/views/RegisterView.vue');
const LogoutView = () => import('@/views/LogoutView.vue');
const InfoPageView = () => import('@/views/InfoPageView.vue');
const ResourcesView = () => import('@/views/ResourcesView.vue');
const ResourceSettingsView = () => import('@/views/ResourceSettingsView.vue');
const ResourceCreateView = () => import('@/views/ResourceCreateView.vue');
const ContentsView = () => import('@/views/ContentsView.vue');
const CorrectionsView = () => import('@/views/CorrectionsView.vue');
const CommunityView = () => import('@/views/CommunityView.vue');

const AccountView = () => import('@/views/account/AccountView.vue');
const AccountSettingsView = () => import('@/views/account/AccountSettingsView.vue');
const AccountMessagesView = () => import('@/views/account/AccountMessagesView.vue');
const VerifyView = () => import('@/views/VerifyView.vue');
const ResetView = () => import('@/views/ResetView.vue');

const TextView = () => import('@/views/admin/TextView.vue');
const NewTextView = () => import('@/views/admin/NewTextView.vue');
const AdminView = () => import('@/views/admin/AdminView.vue');
const AdminSystemUsersView = () => import('@/views/admin/AdminSystemUsersView.vue');
const AdminSystemSettingsView = () => import('@/views/admin/AdminSystemSettingsView.vue');
const AdminSystemMaintenanceView = () => import('@/views/admin/AdminSystemMaintenanceView.vue');
const AdminSystemSegmentsView = () => import('@/views/admin/AdminSystemSegmentsView.vue');

async function _resolveBrowseLocation(
  locationQuery: LocationQuery
): Promise<RouteLocationNamedRaw> {
  const { data, error } = await GET('/locations', {
    params: {
      query: {
        ...Object.fromEntries(
          Object.entries(locationQuery)
            .filter(([_, v]) => v != null)
            .map(([k, v]) => [k, String(v)])
        ),
        // we limit to 2 because this way we know if we got ambiguous results
        // while avoiding to get unnecessarily huge responses...
        limit: 2,
      },
    },
  });
  if (error || !data.length || data.length > 1) {
    const { message } = useMessages();
    message.warning('The location request could not be resolved or produced ambiguous results.');
    return { name: 'browse' };
  } else {
    const state = useStateStore();
    while (!state.pf) await delay();
    return {
      name: 'browse',
      params: {
        textSlug: state.textById(data[0].textId)?.slug || '',
        locId: data[0].id,
      },
    };
  }
}

const router = createRouter({
  history: createWebHistory(env.WEB_PATH),
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'home',
      component: InfoPageView,
      props: {
        pageKey: 'systemHome',
      },
    },
    {
      path: '/texts/:textSlug?/browse/:locId?',
      name: 'browse',
      component: BrowseView,
      props: true,
    },
    {
      path: '/browse',
      name: 'browseResolve',
      component: () => null,
      beforeEnter: async (to) => await _resolveBrowseLocation(to.query),
    },
    {
      path: '/bookmark/:locId+',
      name: 'bookmark',
      component: () => null,
      // only the first locId param is used here and expected to be a valid ID,
      // the others are solely for holding pretty things to please the human eye
      beforeEnter: async (to) => await _resolveBrowseLocation({ locId: to.params.locId[0] }),
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView,
    },
    {
      path: '/search/results',
      name: 'searchResults',
      component: SearchResultsView,
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
      path: '/logout',
      name: 'logout',
      component: LogoutView,
      meta: {
        restricted: 'user',
      },
    },
    {
      path: '/site-notice',
      name: 'siteNotice',
      component: InfoPageView,
      props: {
        pageKey: 'systemSiteNotice',
        icon: SiteNoticeIcon,
      },
    },
    {
      path: '/privacy-policy',
      name: 'privacyPolicy',
      component: InfoPageView,
      props: {
        pageKey: 'systemPrivacyPolicy',
        icon: PrivacyIcon,
      },
    },
    {
      path: '/info/:pageKey?',
      name: 'info',
      component: InfoPageView,
      props: (route) => ({
        pageKey: route.params.pageKey,
        icon: InfoIcon,
      }),
    },
    {
      path: '/users/:username',
      name: 'user',
      component: UserView,
      props: true,
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
      path: '/texts/:textSlug?/resources',
      name: 'resources',
      component: ResourcesView,
      meta: {
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/community',
      name: 'community',
      component: CommunityView,
      meta: {
        restricted: 'user',
      },
    },
    {
      path: '/texts/:textSlug?/resources/:id/settings',
      name: 'resourceSettings',
      component: ResourceSettingsView,
      meta: {
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/texts/:textSlug?/resources/create',
      name: 'resourceCreate',
      component: ResourceCreateView,
      meta: {
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/texts/:textSlug?/resources/:resId/contents/:locId?',
      name: 'resourceContents',
      component: ContentsView,
      meta: {
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/texts/:textSlug?/resources/:resId/corrections',
      name: 'resourceCorrections',
      component: CorrectionsView,
      meta: {
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/account',
      name: 'account',
      redirect: { name: 'accountProfile' },
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
          path: 'settings',
          name: 'accountSettings',
          component: AccountSettingsView,
        },
        {
          path: 'messages',
          name: 'accountMessages',
          component: AccountMessagesView,
        },
      ],
    },
    {
      path: '/texts/:textSlug/settings',
      name: 'textSettings',
      component: TextView,
      props: true,
      meta: {
        restricted: 'superuser',
      },
    },
    {
      path: '/texts/new',
      name: 'newText',
      component: NewTextView,
      meta: {
        restricted: 'superuser',
      },
    },
    {
      path: '/admin',
      name: 'admin',
      redirect: { name: 'adminSettings' },
      component: AdminView,
      meta: {
        restricted: 'superuser',
      },
      children: [
        {
          path: 'settings',
          name: 'adminSettings',
          component: AdminSystemSettingsView,
        },
        {
          path: 'maintenance',
          name: 'adminMaintenance',
          component: AdminSystemMaintenanceView,
        },
        {
          path: 'pages',
          name: 'adminInfoPages',
          component: AdminSystemSegmentsView,
          props: { segmentType: 'info' },
        },
        {
          path: 'segments',
          name: 'adminSegments',
          component: AdminSystemSegmentsView,
          props: { segmentType: 'system' },
        },
        {
          path: 'users',
          name: 'adminUsers',
          component: AdminSystemUsersView,
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

router.beforeEach(async (to, _from) => {
  // enforce route restrictions
  if (to.meta.restricted) {
    const auth = useAuthStore();
    const state = useStateStore();
    while (!state.init.authChecked) await delay(); // wait for session check
    const ru = to.meta.restricted === 'user'; // route is restricted to users
    const rsu = to.meta.restricted === 'superuser'; // route is restricted to superusers
    const l = !!auth.user; // a user is logged in
    const u = auth.user?.isActive && auth.user?.isVerified; // the user is a verified, active user
    const su = auth.user?.isSuperuser; // the user is a superuser
    const authorized = (ru && l && u) || (rsu && l && su);
    // redirect if trying to access a restricted page without authorization
    if (!authorized) {
      const { message } = useMessages();
      message.warning($t('errors.noAccess', { resource: to.path }));
      if (!l) {
        auth.showLoginModal(undefined, to.fullPath, false);
      }
      return { name: 'home' };
    }
  }
  // detect invalid slug
  if ('textSlug' in to.params) {
    const state = useStateStore();
    while (!state.pf) await delay();
    if (!state.pf.texts.find((t) => t.slug === to.params.textSlug)) {
      const { message } = useMessages();
      message.warning($t('errors.invalidSlug', { slug: to.params.textSlug }));
      return { name: 'home' };
    }
  }
  return true;
});

router.afterEach((to, from) => {
  useStateStore().setPageTitle(to);
  if (to.name !== from.name) {
    window.scrollTo(0, 0);
  }
});

export default router;
