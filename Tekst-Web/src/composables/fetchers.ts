import { ref, isRef, unref, watchEffect, type Ref } from 'vue';
import { GET } from '@/api';
import type { UserReadPublic, PlatformStats, UserRead } from '@/api';
import { useDebounceFn } from '@vueuse/core';
import { STATIC_PATH } from '@/common';
import { useMessages } from './messages';
import { $t } from '@/i18n';

export function useProfile(
  usernameOrId: string | Ref<string>,
  active: boolean | Ref<boolean> = true
) {
  const user = ref<UserReadPublic | null>(null);
  const error = ref(false);

  async function fetchProfileData() {
    if (!unref(active)) return;
    user.value = null;
    error.value = false;
    const unoid = unref(usernameOrId);
    if (!unoid) return;

    const { data, error: err } = await GET('/users/public/{user}', {
      params: { path: { user: unoid } },
    });

    if (!err) {
      user.value = data;
    } else {
      error.value = true;
    }
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

  async function load() {
    stats.value = null;
    error.value = false;

    const { data, error: err } = await GET('/platform/stats', {});

    if (!err) {
      stats.value = data;
    } else {
      error.value = true;
    }
  }

  load();

  return { stats, error, load };
}

export function useUsersAdmin() {
  const users = ref<Array<UserRead> | null>(null);
  const error = ref(false);
  const loading = ref(false);

  async function load() {
    loading.value = true;
    users.value = null;
    error.value = false;

    const { data, error: err } = await GET('/users', {});

    if (!err) {
      users.value = data;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  load();

  return {
    users,
    loading,
    error,
    load,
  };
}

export function useUsersSearch(queryRef: Ref<string | null | undefined>) {
  const users = ref<UserReadPublic[]>([]);
  const error = ref(false);
  const loading = ref(false);

  async function load(query?: string | null) {
    if (query == null) {
      users.value = [];
      loading.value = false;
      return;
    }

    loading.value = true;
    users.value = [];
    error.value = false;

    const { data, error: err } = await GET('/users/public', { params: { query: { q: query } } });

    if (!err) {
      users.value = data;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  const debouncedLoad = useDebounceFn(load, 500);
  watchEffect(() => {
    loading.value = true;
    debouncedLoad(unref(queryRef));
  });

  return {
    users,
    loading,
    error,
    load,
  };
}

export function useOskLayout(oskModeKey: Ref<string | null | undefined>) {
  const oskLayout = ref<{ char: string; shift?: string }[][][]>();
  const error = ref(false);
  const loading = ref(false);

  async function load(key?: string | null) {
    oskLayout.value = undefined;

    if (key == null) {
      loading.value = false;
      error.value = true;
      return;
    }

    loading.value = true;
    error.value = false;
    const path = `${STATIC_PATH}/osk/${key}.json`;

    try {
      const response = await fetch(path);
      oskLayout.value = await response.json();
    } catch {
      oskLayout.value = undefined;
      error.value = true;
      const { message } = useMessages();
      message.error($t('osk.msgErrorLoading', { layout: key }), path);
    } finally {
      loading.value = false;
    }
  }

  watchEffect(() => {
    loading.value = true;
    load(unref(oskModeKey));
  });

  return {
    oskLayout,
    loading,
    error,
  };
}
