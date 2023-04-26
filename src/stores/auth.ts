import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { AuthApi, UsersApi, type UserRead } from '@/openapi';
import { useMessagesStore, usePlatformStore } from '@/stores';
import router from '@/router';
import { configureApi } from '@/openApiConfig';
import { useIntervalFn } from '@vueuse/core';
import { i18n } from '@/i18n';

const authApi = configureApi(AuthApi);
const usersApi = configureApi(UsersApi);

function getUserFromLocalStorage(): UserRead | null {
  const storageData = localStorage.getItem('user');
  if (!storageData) return null;
  return JSON.parse(storageData) as UserRead;
}

function useCookieCountdown(cb: () => {}, startNow: boolean = false) {
  const WARN_MINS_BEFORE_COOKIE_EXPIRY = [1, 3, 5, 10];

  const pf = usePlatformStore();
  const messages = useMessagesStore();
  const { t } = i18n.global;

  const authCookieExpiryMs = ref(Number(localStorage.getItem('authCookieExpiry') || -1));
  let warnAheadMinutes = [...WARN_MINS_BEFORE_COOKIE_EXPIRY];
  const getCookieExpiry = () =>
    Date.now() + (pf.data?.security?.authCookieLifetime || 0) * 1000 - 10000;

  const { pause: pauseInterval, resume: resumeInterval } = useIntervalFn(
    () => {
      const now = Date.now();
      // check if expired
      if (now > authCookieExpiryMs.value) {
        cb();
        return;
      }
      // check and warn if expiration is near
      for (const mins of warnAheadMinutes) {
        if ((authCookieExpiryMs.value - now) / 1000 / 60 < mins) {
          warnAheadMinutes.splice(warnAheadMinutes.indexOf(mins));
          messages.warning(t('user.autoLogout', { minutes: mins }), 30);
          return;
        }
      }
    },
    5000,
    { immediate: startNow }
  );

  const startCookieCountdown = () => {
    authCookieExpiryMs.value = getCookieExpiry();
    localStorage.setItem('authCookieExpiry', String(authCookieExpiryMs.value));
    warnAheadMinutes = [...WARN_MINS_BEFORE_COOKIE_EXPIRY];
    resumeInterval();
  };

  const stopCookieCountdown = () => {
    authCookieExpiryMs.value = -1;
    localStorage.removeItem('authCookieExpiry');
    warnAheadMinutes = [];
    pauseInterval();
  };

  return {
    startCookieCountdown,
    stopCookieCountdown,
  };
}

export const useAuthStore = defineStore('auth', () => {
  const messages = useMessagesStore();
  const { t } = i18n.global;

  const user = ref<UserRead | null>(getUserFromLocalStorage());
  const returnUrl = ref<string | null>(null);
  const loggedIn = computed(() => !!user.value);

  // observe auth cookie expiry
  const { startCookieCountdown, stopCookieCountdown } = useCookieCountdown(logout, loggedIn.value);

  // login
  async function login(username: string, password: string) {
    return authApi.authCookieLogin({ username, password }).then(async () => {
      // receive and save user data
      user.value = (await usersApi.usersCurrentUser()).data;
      user.value && localStorage.setItem('user', JSON.stringify(user.value));
      // start cookie expiry monitoring
      startCookieCountdown();
      return user.value;
    });
  }

  // logout
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
      // stop cookie expiry monitoring
      stopCookieCountdown();
      // redirect to login view
      router.push({ name: 'login' });
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
