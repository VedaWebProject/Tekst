import type { PublicUserSearchFilters, UserRead, UserReadPublic, UserSearchFilters } from '@/api';
import { GET } from '@/api';
import { STATIC_PATH } from '@/common';
import { $t } from '@/i18n';
import { useDebounceFn } from '@vueuse/core';
import { isRef, ref, unref, watch, watchEffect, type Ref } from 'vue';
import { useMessages } from './messages';

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

export function useUsersAdmin(filtersRef: Ref<UserSearchFilters>) {
  const users = ref<Array<UserRead>>([]);
  const total = ref(0);
  const error = ref(false);
  const loading = ref(false);

  async function load(filters: UserSearchFilters) {
    loading.value = true;
    users.value = [];
    total.value = 0;
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
    users.value = [];
    total.value = 0;
    error.value = false;

    if (!query.q && !query.emptyOk) {
      loading.value = false;
      return;
    }

    loading.value = true;

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
