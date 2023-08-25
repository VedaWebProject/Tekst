import { ref, isRef, unref, watchEffect, type Ref } from 'vue';
import { GET } from '@/api';
import type { UserReadPublic, LayerNodeCoverage, PlatformStats, UserRead } from '@/api';

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

    const { data, error: err } = await GET('/platform/user/{usernameOrId}', {
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

export function useLayerCoverage(id: string | Ref<string>, active: boolean | Ref<boolean> = true) {
  const coverage = ref<LayerNodeCoverage[] | null>(null);
  const error = ref(false);

  async function fetchCoverageData() {
    if (!unref(active)) return;
    coverage.value = null;
    error.value = false;
    const layerId = unref(id);
    if (!layerId) return;

    const { data, error: err } = await GET('/browse/layers/{id}/coverage', {
      params: { path: { id: layerId } },
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

export function useUsers() {
  const users = ref<Array<UserRead> | null>(null);
  const error = ref(false);

  async function load() {
    users.value = null;
    error.value = false;

    const { data, error: err } = await GET('/admin/users', {});

    if (!err) {
      users.value = data;
    } else {
      error.value = true;
    }
  }

  load();

  return {
    users,
    error,
    load,
  };
}
