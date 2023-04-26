import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { AuthApi, UsersApi, type UserRead } from '@/openapi';
import { useMessagesStore, usePlatformStore } from '@/stores';
import { i18n } from '@/i18n';
import router from '@/router';
import { configureApi } from '@/openApiConfig';

const authApi = configureApi(AuthApi);
const usersApi = configureApi(UsersApi);

function getUserFromLocalStorage(): UserRead | null {
  const storageData = localStorage.getItem('user');
  if (!storageData) return null;
  return JSON.parse(storageData) as UserRead;
}

export const useAuthStore = defineStore('auth', () => {
  const messages = useMessagesStore();
  const pf = usePlatformStore();
  const { t } = i18n.global;

  const user = ref<UserRead | null>(getUserFromLocalStorage());
  const returnUrl = ref<string | null>(null);
  const loggedIn = computed(() => !!user.value);
  const authCookieExpiryMs = ref(Number(localStorage.getItem('authCookieExpiry') || -1));
  const getCookieExpiry = () =>
    Date.now() + (pf.data?.security?.authCookieLifetime || 0) * 1000 - 10000;

  async function login(username: string, password: string) {
    return authApi.authCookieLogin({ username, password }).then(async () => {
      // receive and save user data
      user.value = (await usersApi.usersCurrentUser()).data;
      user.value && localStorage.setItem('user', JSON.stringify(user.value));
      // save cookie expiration time to auto logout after that
      authCookieExpiryMs.value = getCookieExpiry();
      localStorage.setItem('authCookieExpiry', String(authCookieExpiryMs.value));
      return user.value;
    });
  }

  async function logout() {
    try {
      await authApi.authCookieLogout();
      messages.success(t('user.logoutSuccessful'));
    } catch (e) {
      // do sweet FA
    } finally {
      // remove user and auth data
      user.value = null;
      localStorage.removeItem('user');
      authCookieExpiryMs.value = -1;
      localStorage.removeItem('authCookieExpiry');
      // redirect to login view
      router.push({ name: 'login' });
    }
  }

  return {
    user,
    loggedIn,
    returnUrl,
    authCookieExpiryMs,
    login,
    logout,
  };
});
