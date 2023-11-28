import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore, useStateStore } from '@/stores';
import { $t } from '@/i18n';
import { useMessages } from '@/messages';

import GavelOutlined from '@vicons/material/GavelOutlined';
import PrivacyTipOutlined from '@vicons/material/PrivacyTipOutlined';
import InfoOutlined from '@vicons/material/InfoOutlined';

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
const RegisterView = () => import('@/views/RegisterView.vue');
const InfoPageView = () => import('@/views/InfoPageView.vue');
const DataLayersView = () => import('@/views/DataLayersView.vue');
const DataLayerEditView = () => import('@/views/DataLayerEditView.vue');

const AccountView = () => import('@/views/account/AccountView.vue');
const AccountManageView = () => import('@/views/account/AccountManageView.vue');
const VerifyView = () => import('@/views/VerifyView.vue');
const ResetView = () => import('@/views/ResetView.vue');

const AdminView = () => import('@/views/admin/AdminView.vue');
const AdminStatisticsView = () => import('@/views/admin/AdminStatisticsView.vue');
const AdminSystemUsersView = () => import('@/views/admin/AdminSystemUsersView.vue');
const AdminTextsView = () => import('@/views/admin/AdminTextsView.vue');
const AdminTextsGeneralView = () => import('@/views/admin/AdminTextsGeneralView.vue');
const AdminTextsLevelsView = () => import('@/views/admin/AdminTextsLevelsView.vue');
const AdminTextsNodesView = () => import('@/views/admin/AdminTextsNodesView.vue');
const AdminNewTextView = () => import('@/views/admin/AdminNewTextView.vue');
const AdminSystemView = () => import('@/views/admin/AdminSystemView.vue');
const AdminSystemSettingsView = () => import('@/views/admin/AdminSystemSettingsView.vue');
const AdminSystemSegmentsView = () => import('@/views/admin/AdminSystemSegmentsView.vue');
const AdminSystemInfoPagesView = () => import('@/views/admin/AdminSystemInfoPagesView.vue');

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'home',
      component: InfoPageView,
      props: {
        pageKey: 'systemHome',
        icon: InfoOutlined,
      },
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
      path: '/site-notice',
      name: 'siteNotice',
      component: InfoPageView,
      props: {
        pageKey: 'systemSiteNotice',
        icon: GavelOutlined,
      },
    },
    {
      path: '/privacy-policy',
      name: 'privacyPolicy',
      component: InfoPageView,
      props: {
        pageKey: 'systemPrivacyPolicy',
        icon: PrivacyTipOutlined,
      },
    },
    {
      path: '/info/:p',
      name: 'info',
      component: InfoPageView,
      props: {
        icon: InfoOutlined,
      },
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
      path: '/layers/:text',
      name: 'dataLayers',
      component: DataLayersView,
      meta: {
        isTextSpecific: true,
        restricted: 'user',
      },
    },
    {
      path: '/layers/:text/edit/:id',
      name: 'dataLayerEdit',
      component: DataLayerEditView,
      meta: {
        isTextSpecific: true,
        restricted: 'user',
      },
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
              path: 'levels',
              name: 'adminTextsLevels',
              component: AdminTextsLevelsView,
            },
            {
              path: 'nodes',
              name: 'adminTextsNodes',
              component: AdminTextsNodesView,
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
      message.warning($t('errors.noAccess', { resource: to.path }));
      if (auth.loggedIn) {
        next({ name: 'home' });
      } else {
        next(from || { name: 'home' });
        auth.showLoginModal($t('errors.logInToAccess'), to.fullPath, false);
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
