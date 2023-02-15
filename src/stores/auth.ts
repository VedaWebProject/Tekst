import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { UserRead } from 'textrig-ts-client';
import { UserReadFromJSONTyped, AuthApi, UsersApi } from 'textrig-ts-client';
import router from '@/router';

const authApi = new AuthApi();
const usersApi = new UsersApi();

function getUserFromLocalStorage(): UserRead | null {
  const storageData = localStorage.getItem('user');
  if (!storageData) return null;
  return UserReadFromJSONTyped(JSON.parse(storageData), true);
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserRead | null>(getUserFromLocalStorage());
  const returnUrl = ref<string | null>(null);
  const loggedIn = computed(() => !!user);

  async function login(username: string, password: string) {
    await authApi.authCookieLogin({ username, password });
    user.value = await usersApi.usersCurrentUser();
    user.value && localStorage.setItem('user', JSON.stringify(user.value));
    return user.value;
  }

  async function logout() {
    await authApi.authCookieLogout();
    user.value = null;
    localStorage.removeItem('user');
    router.push('/login');
  }

  return {
    user,
    loggedIn,
    returnUrl,
    login,
    logout,
  };
});
