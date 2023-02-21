import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { AuthApi, UsersApi, type UserRead } from '@/openapi';
import { useMessagesStore } from './messages';
import { i18n } from '@/i18n';
import { useRoute } from 'vue-router';
import router from '@/router';

const authApi = new AuthApi();
const usersApi = new UsersApi();
const t = i18n.global.t;

function getUserFromLocalStorage(): UserRead | null {
  const storageData = localStorage.getItem('user');
  if (!storageData) return null;
  return JSON.parse(storageData) as UserRead;
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserRead | null>(getUserFromLocalStorage());
  const returnUrl = ref<string | null>(null);
  const loggedIn = computed(() => !!user.value);
  const messages = useMessagesStore();
  const route = useRoute();

  async function login(username: string, password: string) {
    return authApi.authCookieLogin({ username, password }).then(async () => {
      user.value = (await usersApi.usersCurrentUser()).data;
      user.value && localStorage.setItem('user', JSON.stringify(user.value));
      return user.value;
    });
  }

  async function logout() {
    try {
      await authApi.authCookieLogout();
      messages.success(t('login.logoutSuccessful'));
    } catch (e) {
      // nothing
    } finally {
      user.value = null;
      localStorage.removeItem('user');
      if (route.meta?.restricted) {
        router.push('/home');
      }
    }
  }

  return {
    user,
    loggedIn,
    returnUrl,
    login,
    logout,
  };
});
