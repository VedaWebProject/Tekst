import { ref, isRef, unref, watchEffect, type Ref } from 'vue';
import type { UserReadPublic, PlatformStats, UserRead } from '@/openapi';
import type { AxiosResponse } from 'axios';
import { useApi } from './api';

export function useProfile(
  usernameOrId: string | Ref<string>,
  active: boolean | Ref<boolean> = true
) {
  const user = ref<UserReadPublic | null>(null);
  const error = ref(false);
  const { platformApi } = useApi();

  function fetchProfileData() {
    if (!unref(active)) return;
    user.value = null;
    error.value = false;
    const unoid = unref(usernameOrId);
    if (!unoid) return;
    platformApi
      .getPublicUserInfo({ usernameOrId: unoid })
      .then((response: AxiosResponse<UserReadPublic, any>) => response.data)
      .then((u: UserReadPublic) => (user.value = u))
      .catch(() => (error.value = true));
  }

  if (isRef(usernameOrId) || isRef(active)) {
    watchEffect(fetchProfileData);
  } else {
    fetchProfileData();
  }

  return { user, error };
}

export function useStats() {
  const stats = ref<PlatformStats | null>(null);
  const error = ref(false);
  const { adminApi } = useApi();

  function load() {
    stats.value = null;
    error.value = false;
    adminApi
      .getStats()
      .then((response: AxiosResponse<PlatformStats, any>) => response.data)
      .then((s: PlatformStats) => (stats.value = s))
      .catch(() => (error.value = true));
  }

  load();

  return { stats, error, load };
}

export function useUsers() {
  const users = ref<Array<UserRead> | null>(null);
  const error = ref(false);
  const { adminApi } = useApi();

  function load() {
    users.value = null;
    error.value = false;
    adminApi
      .getUsers()
      .then((response: AxiosResponse<Array<UserRead>, any>) => response.data)
      .then((u: Array<UserRead>) => (users.value = u))
      .catch(() => (error.value = true));
  }

  load();

  return {
    users,
    error,
    load,
  };
}
