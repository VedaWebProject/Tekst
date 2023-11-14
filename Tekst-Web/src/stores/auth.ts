import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { UserRead, UserUpdate } from '@/api';
import { useMessages } from '@/messages';
import { GET, PATCH, POST, optionsPresets } from '@/api/index';
import { $t, localeProfiles } from '@/i18n';
import { useIntervalFn } from '@vueuse/core';
import { useRouter, type RouteLocationRaw } from 'vue-router';
import { usePlatformData } from '@/platformData';
import { useStateStore } from '@/stores';
import { LoginTemplatePromise } from '@/templatePromises';

const SESSION_POLL_INTERVAL_S = 60; // check session expiry every n seconds
const SESSION_EXPIRY_OFFSET_S = 10; // assume session expired n seconds early
const SESSION_WARN_AHEAD_S = 600; // start showing warnings n seconds before expiry

function getUserFromLocalStorage() {
  const storageData = localStorage.getItem('user');
  if (!storageData) return;
  return JSON.parse(storageData) as UserRead;
}

const { pause: _stopSessionCheck, resume: _startSessionCheck } = useIntervalFn(
  () => {
    const { checkSession } = useAuthStore();
    checkSession();
  },
  SESSION_POLL_INTERVAL_S * 1000,
  { immediate: true, immediateCallback: false }
);

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  const { pfData, loadPlatformData } = usePlatformData();
  const { message } = useMessages();
  const state = useStateStore();

  const user = ref(getUserFromLocalStorage());
  const loggedIn = computed(() => !!user.value);

  const sessionExpiryTsSec = ref(
    Number(localStorage.getItem('sessionExpiryS') || Number.MAX_SAFE_INTEGER)
  );

  function _setCookieExpiry() {
    sessionExpiryTsSec.value =
      Date.now() / 1000 +
      (pfData.value?.security?.authCookieLifetime || 0) -
      SESSION_EXPIRY_OFFSET_S;
    localStorage.setItem('sessionExpiryS', String(sessionExpiryTsSec.value));
  }

  function _unsetCookieExpiry() {
    sessionExpiryTsSec.value = Number.MAX_SAFE_INTEGER;
    localStorage.removeItem('sessionExpiryS');
  }

  async function _renewExpiredSession() {
    message.warning($t('account.sessionExpired'));
    _cleanupSession();
    if (!(await showLoginModal($t('account.renewLogin'), router.currentRoute.value, false))) {
      router.push({ name: 'home' });
    }
  }

  function _cleanupSession() {
    user.value = undefined;
    localStorage.removeItem('user');
    _unsetCookieExpiry();
    _stopSessionCheck();
  }

  function _sessionExpiresInS() {
    return sessionExpiryTsSec.value - Date.now() / 1000;
  }

  function checkSession() {
    const timeLeftS = _sessionExpiresInS();
    if (timeLeftS <= 0) {
      _renewExpiredSession();
      return;
    } else if (timeLeftS <= SESSION_WARN_AHEAD_S) {
      const minutes = Math.floor(timeLeftS / 60);
      const seconds = Math.round(timeLeftS % 60);
      message.warning($t('account.autoLogout', { minutes, seconds }), undefined, 30);
    }
  }

  async function showLoginModal(
    message: string | undefined = undefined,
    nextRoute: RouteLocationRaw = { name: 'home' },
    showRegisterLink: boolean = true
  ) {
    try {
      return await LoginTemplatePromise.start(message, nextRoute, showRegisterLink);
    } catch {
      return false;
    }
  }

  async function login(
    username: string,
    password: string,
    nextRoute: RouteLocationRaw | null | undefined
  ) {
    // login
    const { error } = await POST('/auth/cookie/login', {
      body: { username, password },
      ...optionsPresets.formUrlEncoded,
    });

    if (!error) {
      // init session
      _setCookieExpiry();
      _startSessionCheck();
      // load user data
      const { data: userData, error: userError } = await GET('/users/me', {});
      if (userError) {
        message.error($t('errors.unexpected'), error);
        _cleanupSession();
        return false;
      }
      localStorage.setItem('user', JSON.stringify(userData));
      user.value = userData;
      // load fresh platform data
      await loadPlatformData();
      // process user locale
      if (!userData.locale) {
        updateUser({ locale: localeProfiles[state.locale].key }); // no need to wait
      } else if (userData.locale !== state.locale) {
        await state.setLocale(userData.locale, false);
        message.info(
          $t('account.localeApplied', {
            locale: localeProfiles[userData.locale].displayFull,
          })
        );
      }
      message.success($t('general.welcome', { name: userData.firstName }));
      nextRoute && router.push(nextRoute);
      return true;
    } else {
      if (error.detail === 'LOGIN_BAD_CREDENTIALS') {
        message.error($t('account.errors.badCreds'));
      } else if (error.detail === 'LOGIN_USER_NOT_VERIFIED') {
        const { error } = await POST('/auth/request-verify-token', { body: { email: username } });
        if (!error) {
          message.error($t('account.errors.notVerified'));
        } else {
          message.error($t('errors.unexpected'), error);
        }
      } else {
        message.error($t('errors.unexpected'), error);
      }
      _cleanupSession();
      return false;
    }
  }

  async function logout() {
    router.push({ name: 'home' });
    if (!(await POST('/auth/cookie/logout', {})).error) {
      message.success($t('account.logoutSuccessful'));
    }
    _cleanupSession();
    // reload platform data as some resources might not be accessible anymore
    await loadPlatformData();
    if (!pfData.value?.texts.find((t) => t.id === state.text?.id)) {
      state.text =
        pfData.value?.texts.find((t) => t.id === pfData.value?.settings.defaultTextId) ||
        pfData.value?.texts[0];
    }
  }

  async function updateUser(userUpdate: UserUpdate) {
    if (!user.value) return Promise.reject('no user');
    const { data: updatedUser, error } = await PATCH('/users/me', { body: userUpdate });
    if (!error) {
      user.value = updatedUser;
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return updatedUser;
    } else {
      throw error;
    }
  }

  return {
    user,
    loggedIn,
    showLoginModal,
    login,
    logout,
    updateUser,
    checkSession,
  };
});
