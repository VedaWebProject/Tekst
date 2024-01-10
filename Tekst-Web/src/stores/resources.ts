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

  function sortResources(res: AnyResourceRead[]) {
    return res.sort((a, b) => (a.config?.sortOrder ?? 0) - (b.config?.sortOrder ?? 0));
  }

  async function load() {
    if (loading.value || !state.text) {
      return;
    }
    loading.value = true;
    error.value = false;

    const { data, error: err } = await GET('/resources', {
      params: {
        query: {
          txt: state.text.id,
        },
      },
    });

    if (!err) {
      resources.value = sortResources(
        data.map((r) => {
          const existingResource = resources.value.find((re) => re.id === r.id);
          return {
            ...r,
            active: existingResource ? existingResource.active : r.config?.defaultActive,
            units: existingResource?.units || [],
          };
        })
      );
      error.value = false;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  function replace(resource: AnyResourceRead) {
    if (resources.value.find((re) => re.id === resource.id)) {
      resources.value = sortResources(
        resources.value.map((r) =>
          r.id === resource.id ? { ...resource, active: r.active, units: r.units } : r
        )
      );
    } else {
      add(resource);
    }
  }

  function add(resource: AnyResourceRead) {
    resource.active = resource.config?.defaultActive;
    resources.value = sortResources(resources.value.concat([resource]));
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

  function resetCoverage(resourceId?: string) {
    if (!resourceId) return;
    const res = resources.value.find((l) => l.id === resourceId);
    if (!res) return;
    res.coverage = undefined;
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
    resetCoverage,
  };
});
