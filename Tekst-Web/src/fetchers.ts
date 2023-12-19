import { ref, isRef, unref, watchEffect, type Ref } from 'vue';
import { GET } from '@/api';
import type { UserReadPublic, ResourceNodeCoverage, PlatformStats, UserRead } from '@/api';
import { useDebounceFn } from '@vueuse/core';

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

    const { data, error: err } = await GET('/platform/users/{usernameOrId}', {
      params: { path: { usernameOrId: unoid } },
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

export function useResourceCoverage(
  id: string | Ref<string>,
  active: boolean | Ref<boolean> = true
) {
  const coverage = ref<ResourceNodeCoverage[] | null>(null);
  const error = ref(false);

  async function fetchCoverageData() {
    if (!unref(active)) return;
    coverage.value = null;
    error.value = false;
    const resourceId = unref(id);
    if (!resourceId) return;

    const { data, error: err } = await GET('/browse/resources/{id}/coverage', {
      params: { path: { id: resourceId } },
    });

    if (!err) {
      coverage.value = data;
    } else {
      error.value = true;
    }
  }

  if (isRef(id) || isRef(active)) {
    watchEffect(fetchCoverageData);
  } else {
    fetchCoverageData();
  }

  return { coverage, error };
}

export function useStats() {
  const stats = ref<PlatformStats | null>(null);
  const error = ref(false);

  async function load() {
    stats.value = null;
    error.value = false;

    const { data, error: err } = await GET('/admin/stats', {});

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

    const { data, error: err } = await GET('/admin/users', {});

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

    const { data, error: err } = await GET('/platform/users', { params: { query: { q: query } } });

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
