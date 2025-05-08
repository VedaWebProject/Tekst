import type { UserRead, UserUpdate } from '@/api';
import { GET, PATCH, POST, optionsPresets } from '@/api/index';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { $t } from '@/i18n';
import { useResourcesStore, useSearchStore, useStateStore, useUserMessagesStore } from '@/stores';
import { useIntervalFn, useSessionStorage } from '@vueuse/core';
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useRouter, type RouteLocationRaw } from 'vue-router';

const _SES_CHK_INTV_S = 60; // check session expiry every n seconds
const _SES_EXP_OFF_S = 10; // assume session expired n seconds early
const _SES_WARN_AHEAD_S = 600; // start showing warnings n seconds before expiry

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  const resources = useResourcesStore();
  const { loadPlatformData } = usePlatformData();
  const { message } = useMessages();
  const state = useStateStore();
  const search = useSearchStore();
  const userMessages = useUserMessagesStore();

  const user = ref<UserRead>();

  const sessionExpiryTsSec = useSessionStorage('sessionExpiryS', Number.MAX_SAFE_INTEGER);

  const { pause: _stopSessionCheck, resume: _startSessionCheck } = useIntervalFn(
    async () => {
      const { checkSession } = useAuthStore();
      await checkSession();
    },
    _SES_CHK_INTV_S * 1000,
    { immediate: true, immediateCallback: false }
  );

  function _setCookieExpiry() {
    sessionExpiryTsSec.value =
      Date.now() / 1000 + (state.pf?.security.authCookieLifetime || 0) - _SES_EXP_OFF_S;
  }

  function _unsetCookieExpiry() {
    sessionExpiryTsSec.value = Number.MAX_SAFE_INTEGER;
  }

  function _cleanupSession() {
    user.value = undefined;
    userMessages.stopThreadsPolling();
    _unsetCookieExpiry();
    _stopSessionCheck();
    search.currentRequest = undefined;
  }

  function _sessionExpiresInS() {
    return sessionExpiryTsSec.value ? sessionExpiryTsSec.value - Date.now() / 1000 : 0;
  }

  async function checkSession() {
    const timeLeftS = _sessionExpiresInS();
    if (timeLeftS <= 0) {
      message.warning($t('account.sessionExpired'));
      const currRoute = router.currentRoute.value;
      await logout();
      showLoginModal($t('account.renewLogin'), currRoute, false);
    } else if (timeLeftS <= _SES_WARN_AHEAD_S) {
      const minutes = Math.floor(timeLeftS / 60);
      const seconds = Math.round(timeLeftS % 60);
      message.warning($t('account.autoLogout', { minutes, seconds }), undefined, 30);
    }
  }

  function showLoginModal(
    message?: string,
    nextRoute: RouteLocationRaw = { name: 'home' },
    showRegisterLink: boolean = true
  ) {
    loginModalState.value = {
      show: true,
      message: message,
      nextRoute: nextRoute,
      showRegisterLink: showRegisterLink,
    };
  }

  function closeLoginModal(gotoNextRoute: boolean = true) {
    if (gotoNextRoute && loginModalState.value.nextRoute) {
      router.replace(loginModalState.value.nextRoute);
    }
    loginModalState.value = {};
  }

  async function _loadUserData() {
    // load core user data
    const { data, error } = await GET('/users/me', {});
    if (!error) {
      user.value = data;
      return user.value;
    }
  }

  async function login(username: string, password: string, persistent: boolean = false) {
    loginModalState.value.loading = true;
    // login
    const { error } = await POST('/auth/cookie/login', {
      body: { username, password, scope: '', persistent },
      ...optionsPresets.formUrlEncoded,
    });

    if (!error) {
      // init session
      _setCookieExpiry();
      _startSessionCheck();
      const userData = await _loadUserData();
      if (!userData) return;
      await loadPlatformData();
      await resources.load();
      // process user locale
      if (!userData.locale) {
        updateUser({ locale: state.locale }); // no need to wait
      } else if (userData.locale !== state.locale) {
        await state.setLocale(userData.locale, false);
      }
      userMessages.startThreadsPolling();
      // welcome
      if (userData.seen) {
        message.success($t('account.welcome', { name: userData.name }), undefined, 3);
      } else {
        message.success($t('account.welcomeFirstTime', { name: userData.name }), undefined, 30);
      }
      closeLoginModal();
      return true;
    } else {
      if (error.detail === 'LOGIN_USER_NOT_VERIFIED') {
        await POST('/auth/request-verify-token', { body: { email: username } });
      }
      _cleanupSession();
      closeLoginModal(false);
      return false;
    }
  }

  async function logout(noMsg?: boolean) {
    router.push({ name: 'home' });
    if (!(await POST('/auth/cookie/logout', {})).error && !noMsg) {
      message.success($t('account.logoutSuccessful'));
    }
    _cleanupSession();
    await loadPlatformData(); // reload platform data as some resources might not be accessible anymore
    if (!state.pf?.texts.find((t) => t.id === state.text?.id)) {
      router.replace({
        name: 'browse',
        params: { textSlug: state.defaultText?.slug },
      });
    }
    await resources.load();
  }

  async function updateUser(userUpdate: UserUpdate) {
    if (!user.value) return Promise.reject('no user');
    const { data: updatedUser, error } = await PATCH('/users/me', { body: userUpdate });
    if (!error) {
      user.value = updatedUser;
      return updatedUser;
    }
  }

  // login modal state and handlers

  const loginModalState = ref<{
    show?: boolean;
    loading?: boolean;
    message?: string;
    nextRoute?: RouteLocationRaw;
    showRegisterLink?: boolean;
  }>({
    show: false,
  });

  return {
    user,
    showLoginModal,
    closeLoginModal,
    loginModalState,
    login,
    logout,
    updateUser,
    checkSession,
  };
});
