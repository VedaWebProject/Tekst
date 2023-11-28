import { ref, isRef, unref, watchEffect, type Ref } from 'vue';
import { GET } from '@/api';
import type {
  UserReadPublic,
  LayerNodeCoverage,
  PlatformStats,
  UserRead,
  AnyLayerRead,
} from '@/api';

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

export function useUsersPublic() {
  const users = ref<Array<UserReadPublic> | null>(null);
  const error = ref(false);
  const loading = ref(false);

  async function load() {
    loading.value = true;
    users.value = null;
    error.value = false;

    const { data, error: err } = await GET('/platform/users', {});

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

export function useLayers(
  textId: string | Ref<string>,
  includeOwners: boolean = true,
  includeWritable: boolean = true,
  includeShares: boolean = true
) {
  const layers = ref<AnyLayerRead[]>([]);
  const error = ref(false);
  const loading = ref(false);

  async function load() {
    loading.value = true;
    layers.value = [];
    error.value = false;

    const { data, error: err } = await GET('/layers', {
      params: {
        query: {
          textId: unref(textId),
          owners: includeOwners,
          writable: includeWritable,
          shares: includeShares,
        },
      },
    });

    if (!err) {
      layers.value = data;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  if (isRef(textId)) {
    watchEffect(load);
  } else {
    load();
  }

  return {
    layers,
    error,
    loading,
    load,
  };
}
