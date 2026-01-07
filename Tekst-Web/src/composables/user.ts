import type { PublicUserSearchFilters, UserReadPublic } from '@/api';
import { GET } from '@/api';
import { useDebounceFn } from '@vueuse/core';
import { isRef, ref, unref, watch, watchEffect, type Ref } from 'vue';

const _cache = new Map<string, UserReadPublic>();

export function useUser(usernameOrId: string | Ref<string>) {
  const user = ref<UserReadPublic | null>(null);
  const error = ref(false);
  const loading = ref(false);

  async function fetchUserData() {
    loading.value = true;
    error.value = false;
    const unoid = unref(usernameOrId);
    if (!unoid) {
      error.value = true;
      loading.value = false;
      return;
    }

    // get from cache
    user.value = _cache.get(unoid) || null;
    if (!!user.value) {
      loading.value = false;
      return;
    }

    // get from api
    const { data, error: err } = await GET('/users/public/{user}', {
      params: { path: { user: unoid } },
    });

    if (!err) {
      _cache.set(unoid, data);
      user.value = data;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  if (isRef(usernameOrId)) {
    watchEffect(fetchUserData);
  } else {
    fetchUserData();
  }

  return { user, loading, error };
}

export function usePublicUserSearch(queryRef: Ref<PublicUserSearchFilters>) {
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
