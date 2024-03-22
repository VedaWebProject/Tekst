import { ref, isRef, unref, watchEffect, type Ref, watch } from 'vue';
import { GET } from '@/api';
import type {
  UserReadPublic,
  PlatformStats,
  UserRead,
  UserSearchFilters,
  PublicUserSearchFilters,
} from '@/api';
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

export function useUsersAdmin(filtersRef: Ref<UserSearchFilters>) {
  const users = ref<Array<UserRead>>([]);
  const total = ref(0);
  const error = ref(false);
  const loading = ref(false);

  async function load(filters: UserSearchFilters) {
    loading.value = true;
    users.value = [];
    error.value = false;

    const { data, error: e } = await GET('/users', {
      params: {
        query: filters,
      },
    });

    if (!e) {
      users.value = data.users || [];
      total.value = data.total || 0;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  const debouncedLoad = useDebounceFn(load, 500);

  watch(
    filtersRef,
    (newFilters) => {
      loading.value = true;
      debouncedLoad(newFilters);
    },
    { immediate: true, deep: true }
  );

  return {
    users,
    total,
    loading,
    error,
    load,
  };
}

export function useUsersSearch(queryRef: Ref<PublicUserSearchFilters>) {
  const users = ref<UserReadPublic[]>([]);
  const error = ref(false);
  const loading = ref(false);
  const total = ref(0);

  async function load(query: PublicUserSearchFilters) {
    if (!query.q && !query.emptyOk) {
      users.value = [];
      loading.value = false;
      return;
    }

    loading.value = true;
    users.value = [];
    error.value = false;

    const { data, error: err } = await GET('/users/public', { params: { query: query } });

    if (!err) {
      users.value = data.users || [];
      total.value = data.total || 0;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  const debouncedLoad = useDebounceFn(load, 500);

  watch(
    queryRef,
    (newQuery) => {
      loading.value = true;
      debouncedLoad(newQuery);
    },
    { immediate: true, deep: true }
  );

  return {
    users,
    total,
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
