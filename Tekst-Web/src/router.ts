import { WEB_PATH } from '@/common';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { InfoIcon, PrivacyIcon, SiteNoticeIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { delay } from '@/utils';
import { createRouter, createWebHistory } from 'vue-router';

declare module 'vue-router' {
  interface RouteMeta {
    restricted?: 'user' | 'superuser';
    isTextSpecific?: boolean;
  }
}

const UserView = () => import('@/views/UserView.vue');
const HelpView = () => import('@/views/HelpView.vue');
const BrowseView = () => import('@/views/BrowseView.vue');
const SearchView = () => import('@/views/SearchView.vue');
const SearchResultsView = () => import('@/views/SearchResultsView.vue');
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

const AdminView = () => import('@/views/admin/AdminView.vue');
const AdminStatisticsView = () => import('@/views/admin/AdminStatisticsView.vue');
const AdminSystemUsersView = () => import('@/views/admin/AdminSystemUsersView.vue');
const AdminTextsView = () => import('@/views/admin/AdminTextsView.vue');
const AdminTextsSettingsView = () => import('@/views/admin/AdminTextsSettingsView.vue');
const AdminTextsLevelsView = () => import('@/views/admin/AdminTextsLevelsView.vue');
const AdminTextsLocationsView = () => import('@/views/admin/AdminTextsLocationsView.vue');
const AdminNewTextView = () => import('@/views/admin/AdminNewTextView.vue');
const AdminSystemView = () => import('@/views/admin/AdminSystemView.vue');
const AdminSystemSettingsView = () => import('@/views/admin/AdminSystemSettingsView.vue');
const AdminSystemMaintenanceView = () => import('@/views/admin/AdminSystemMaintenanceView.vue');
const AdminSystemSegmentsView = () => import('@/views/admin/AdminSystemSegmentsView.vue');
const AdminSystemInfoPagesView = () => import('@/views/admin/AdminSystemInfoPagesView.vue');

const router = createRouter({
  history: createWebHistory(WEB_PATH),
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
      path: '/text/:textSlug?/browse/:locId?',
      name: 'browse',
      component: BrowseView,
      meta: {
        isTextSpecific: true,
      },
      props: true,
    },
    {
      path: '/text/:textSlug?/search',
      name: 'search',
      component: SearchView,
    },
    {
      path: '/search',
      name: 'searchResults',
      component: SearchResultsView,
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
      path: '/user/:username',
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
      path: '/text/:textSlug?/resources',
      name: 'resources',
      component: ResourcesView,
      meta: {
        isTextSpecific: true,
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
      path: '/text/:textSlug?/resources/:id/settings',
      name: 'resourceSettings',
      component: ResourceSettingsView,
      meta: {
        isTextSpecific: true,
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/text/:textSlug?/resources/create',
      name: 'resourceCreate',
      component: ResourceCreateView,
      meta: {
        isTextSpecific: true,
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/text/:textSlug?/resources/:resId/contents/:locId?',
      name: 'resourceContents',
      component: ContentsView,
      meta: {
        isTextSpecific: true,
        restricted: 'user',
      },
      props: true,
    },
    {
      path: '/text/:textSlug?/resources/:resId/corrections',
      name: 'resourceCorrections',
      component: CorrectionsView,
      meta: {
        isTextSpecific: true,
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
          path: 'texts/:textSlug',
          name: 'adminTexts',
          redirect: { name: 'adminTextsSettings' },
          component: AdminTextsView,
          meta: {
            isTextSpecific: true,
          },
          children: [
            {
              path: 'general',
              name: 'adminTextsSettings',
              component: AdminTextsSettingsView,
            },
            {
              path: 'levels',
              name: 'adminTextsLevels',
              component: AdminTextsLevelsView,
            },
            {
              path: 'locations',
              name: 'adminTextsLocations',
              component: AdminTextsLocationsView,
            },
          ],
        },
        {
          path: 'new-text',
          name: 'adminNewText',
          component: AdminNewTextView,
        },
        {
          path: 'system',
          name: 'adminSystem',
          redirect: { name: 'adminSystemSettings' },
          component: AdminSystemView,
          children: [
            {
              path: 'settings',
              name: 'adminSystemSettings',
              component: AdminSystemSettingsView,
            },
            {
              path: 'maintenance',
              name: 'adminSystemMaintenance',
              component: AdminSystemMaintenanceView,
            },
            {
              path: 'pages',
              name: 'adminSystemInfoPages',
              component: AdminSystemInfoPagesView,
            },
            {
              path: 'segments',
              name: 'adminSystemSegments',
              component: AdminSystemSegmentsView,
            },
            {
              path: 'users',
              name: 'adminSystemUsers',
              component: AdminSystemUsersView,
            },
          ],
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

router.beforeEach(async (to, from, next) => {
  // enforce route restrictions
  if (to.meta.restricted) {
    const auth = useAuthStore();
    const state = useStateStore();
    while (!state.init.authChecked) {
      await delay(50);
    }
    const ru = to.meta.restricted === 'user'; // route is restricted to users
    const rsu = to.meta.restricted === 'superuser'; // route is restricted to superusers
    const l = auth.loggedIn; // a user is logged in
    const u = auth.user?.isActive && auth.user?.isVerified; // the user is a verified, active user
    const su = auth.user?.isSuperuser; // the user is a superuser
    const authorized = (ru && l && u) || (rsu && l && su);
    // redirect if trying to access a restricted page without authorization
    if (!authorized) {
      const { message } = useMessages();
      message.warning($t('errors.noAccess', { resource: to.path }));
      next({ name: 'home' });
      if (!auth.loggedIn) {
        auth.showLoginModal(undefined, to.fullPath, false);
      }
      return; // this is important!
    }
  }
  // proceed to next hook in router pipeline
  next();
});

router.afterEach((to, from) => {
  useStateStore().setPageTitle(to);
  if (to.name !== from.name) {
    window.scrollTo(0, 0);
  }
});

export default router;
