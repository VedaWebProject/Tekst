import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore, useMessagesStore } from '@/stores';
import { HomeView, AboutView, AccountView } from '@/views';

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
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/account',
      name: 'account',
      component: AccountView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: HomeView,
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

router.beforeEach(async (to) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const auth = useAuthStore();
  const messages = useMessagesStore();
  const restrictedPages = ['/admin', '/account'];
  const authRequired = restrictedPages.includes(to.path);

  if (authRequired && !auth.user) {
    auth.returnUrl = to.fullPath;
    messages.warning("You don't have access to this page.");
    return '/home';
  }
});

export default router;
