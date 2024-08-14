import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { UserRead, UserUpdate } from '@/api';
import { useMessages } from '@/composables/messages';
import { GET, PATCH, POST, optionsPresets } from '@/api/index';
import { $t } from '@/i18n';
import { useIntervalFn } from '@vueuse/core';
import { useRouter, type RouteLocationRaw } from 'vue-router';
import { usePlatformData } from '@/composables/platformData';
import { useResourcesStore, useStateStore, useUserMessagesStore } from '@/stores';

const SESSION_POLL_INTERVAL_S = 60; // check session expiry every n seconds
const SESSION_EXPIRY_OFFSET_S = 10; // assume session expired n seconds early
const SESSION_WARN_AHEAD_S = 600; // start showing warnings n seconds before expiry

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
  const resources = useResourcesStore();
  const { pfData, loadPlatformData } = usePlatformData();
  const { message } = useMessages();
  const state = useStateStore();
  const userMessages = useUserMessagesStore();

  const user = ref<UserRead>();
  const loggedIn = computed(() => !!user.value);

  const sessionExpiryTsSec = ref(
    Number(localStorage.getItem('sessionExpiryS')) || Number.MAX_SAFE_INTEGER
  );

  async function loadExistingSession() {
    const userData = localStorage.getItem('user');
    if (userData) {
      user.value = JSON.parse(userData) as UserRead;
      await _loadUserData();
    }
  }

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
    showLoginModal($t('account.renewLogin'), router.currentRoute.value, false);
  }

  function _cleanupSession() {
    user.value = undefined;
    localStorage.removeItem('user');
    userMessages.stopThreadsPolling();
    _unsetCookieExpiry();
    _stopSessionCheck();
  }

  function _sessionExpiresInS() {
    return sessionExpiryTsSec.value ? sessionExpiryTsSec.value - Date.now() / 1000 : 0;
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
    gotoNextRoute &&
      loginModalState.value.nextRoute &&
      router.replace(loginModalState.value.nextRoute);
    loginModalState.value = {};
  }

  async function _loadUserData() {
    // load core user data
    const { data, error } = await GET('/users/me', {});
    if (!error) {
      user.value = data;
      localStorage.setItem('user', JSON.stringify(user.value));
      return user.value;
    } else {
      logout();
    }
  }

  async function login(username: string, password: string) {
    loginModalState.value.loading = true;
    // login
    const { error } = await POST('/auth/cookie/login', {
      body: { username, password },
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
    if (!(await POST('/auth/cookie/logout', {})).error) {
      !noMsg && message.success($t('account.logoutSuccessful'));
    }
    _cleanupSession();
    await loadPlatformData(); // reload platform data as some resources might not be accessible anymore
    if (!pfData.value?.texts.find((t) => t.id === state.text?.id)) {
      state.text =
        pfData.value?.texts.find((t) => t.id === pfData.value?.state.defaultTextId) ||
        pfData.value?.texts[0];
    }
    await resources.load();
  }

  async function updateUser(userUpdate: UserUpdate) {
    if (!user.value) return Promise.reject('no user');
    const { data: updatedUser, error } = await PATCH('/users/me', { body: userUpdate });
    if (!error) {
      user.value = updatedUser;
      localStorage.setItem('user', JSON.stringify(updatedUser));
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
    loggedIn,
    loadExistingSession,
    showLoginModal,
    closeLoginModal,
    loginModalState,
    login,
    logout,
    updateUser,
    checkSession,
  };
});
