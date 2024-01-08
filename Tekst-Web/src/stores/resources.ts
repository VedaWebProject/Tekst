import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { GET, type AnyResourceRead, type ResourceCoverage } from '@/api';
import { useAuthStore, useStateStore } from '@/stores';

export const useResourcesStore = defineStore('resources', () => {
  const state = useStateStore();
  const auth = useAuthStore();

  const resources = ref<AnyResourceRead[]>([]);
  const error = ref(false);

  const loading = ref(false);

  async function load() {
    if (loading.value || !state.text) {
      return;
    }
    loading.value = true;
    error.value = false;

    const { data, error: err } = await GET('/resources', {
      params: {
        query: {
          textId: state.text.id,
        },
      },
    });

    if (!err) {
      resources.value = data
        .map((l) => {
          const existingResource = resources.value.find((lo) => lo.id === l.id);
          return {
            ...l,
            active: !existingResource || existingResource.active,
            units: existingResource?.units || [],
          };
        })
        .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0));
      error.value = false;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  function replace(resource: AnyResourceRead) {
    resources.value = resources.value
      .map((l) => (l.id === resource.id ? resource : l))
      .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0));
  }

  function add(resource: AnyResourceRead) {
    resources.value = resources.value
      .concat([resource])
      .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0));
  }

  async function getCoverage(resourceId: string): Promise<ResourceCoverage | undefined> {
    const res = resources.value.find((l) => l.id === resourceId);
    if (!res) return;
    const cov = res?.coverage;
    if (cov) return cov;
    const { data } = await GET('/browse/resources/{id}/coverage', {
      params: { path: { id: resourceId } },
    });
    if (!data) return;
    res.coverage = data;
    return data;
  }

  // watch for events that trigger a reload of resources data
  watch(
    [() => auth.loggedIn, () => state.text],
    () => {
      load();
    },
    { immediate: true }
  );

  return {
    data: resources,
    error,
    loading,
    load,
    replace,
    add,
    getCoverage,
  };
});
