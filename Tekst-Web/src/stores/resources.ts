import {
  GET,
  type AnnotationAggregation,
  type AnyContentRead,
  type AnyResourceRead,
  type CorrectionRead,
  type ResourceCoverage,
} from '@/api';
import { useStateStore } from '@/stores';
import { hashCode, pickTranslation } from '@/utils';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useResourcesStore = defineStore('resources', () => {
  const state = useStateStore();

  const resourcesAll = ref<AnyResourceRead[]>([]);
  const resourcesOfText = computed(() =>
    resourcesAll.value.filter((r) => r.textId === state.text?.id)
  );
  const resourceTitles = computed(() =>
    Object.fromEntries(
      resourcesAll.value.map((r) => [r.id, pickTranslation(r.title, state.locale)])
    )
  );
  const aggregations = ref<Record<string, AnnotationAggregation[]>>({});
  const coverage = ref<Record<string, ResourceCoverage>>({});
  const corrections = ref<Record<string, CorrectionRead[]>>({});
  const correctionsCount = computed<Record<string, number>>(() =>
    Object.fromEntries(resourcesAll.value.map((r) => [r.id, r.corrections || 0]))
  );
  const correctionsCountTotal = computed(() =>
    Object.values(correctionsCount.value).reduce((a, b) => a + b, 0)
  );
  const dataHash = computed(() => hashCode(resourcesAll.value));
  const error = ref(false);

  const loading = ref(false);

  function sortResources(res: AnyResourceRead[]) {
    return res.sort((a, b) => (a.config.common.sortOrder ?? 0) - (b.config.common.sortOrder ?? 0));
  }

  async function load() {
    if (loading.value) {
      return;
    }
    loading.value = true;
    error.value = false;

    const { data, error: err } = await GET('/resources'); // fetch ALL resources

    if (!err) {
      resourcesAll.value = sortResources(
        data.map((r) => {
          const existingResource = resourcesAll.value.find((re) => re.id === r.id);
          return {
            ...r,
            active: !!existingResource?.active || !!r.config.common.defaultActive,
            contents: existingResource?.contents ?? [],
          };
        })
      );
      error.value = false;
    } else {
      error.value = true;
    }
    corrections.value = {};
    loading.value = false;
  }

  async function loadCorrections(resourceId: string) {
    const { data, error } = await GET('/corrections/{resourceId}', {
      params: { path: { resourceId } },
    });
    if (!error) {
      corrections.value[resourceId] = data.sort((a, b) => Date.parse(b.date) - Date.parse(a.date));
    } else {
      corrections.value[resourceId] = [];
    }
  }

  function replace(resource: AnyResourceRead) {
    if (resourcesAll.value.find((re) => re.id === resource.id)) {
      resourcesAll.value = sortResources(
        resourcesAll.value.map((r) =>
          r.id === resource.id ? { ...resource, active: r.active, contents: r.contents } : r
        )
      );
    } else {
      add(resource);
    }
  }

  function add(resource: AnyResourceRead) {
    resource.active = resource.config.common.defaultActive;
    resourcesAll.value = sortResources(resourcesAll.value.concat([resource]));
  }

  function remove(resourceId: string) {
    resourcesAll.value = resourcesAll.value.filter((r) => r.id !== resourceId);
  }

  async function getAggregations(resourceId: string): Promise<AnnotationAggregation[]> {
    if (!resourcesAll.value.find((r) => r.id === resourceId)) return [];
    const agg = aggregations.value[resourceId];
    if (agg) return agg;
    const { data, error } = await GET('/resources/{id}/aggregations', {
      params: { path: { id: resourceId } },
    });
    if (!error && !!data) {
      aggregations.value[resourceId] = data;
      return data;
    } else {
      aggregations.value[resourceId] = [];
      return [];
    }
  }

  function applyContents(contents: AnyContentRead[]) {
    resourcesAll.value
      .filter((r) => contents.map((c) => c.resourceId).includes(r.id))
      .forEach((r) => {
        r.contents = contents.filter((c) => c.resourceId === r.id) ?? [];
      });
  }

  async function getCoverage(resourceId: string): Promise<ResourceCoverage | undefined> {
    if (!resourcesAll.value.find((r) => r.id === resourceId)) return undefined;
    const cov = coverage.value[resourceId];
    if (cov) return cov;
    const { data, error } = await GET('/resources/{id}/coverage', {
      params: { path: { id: resourceId } },
    });
    if (!error && !!data) {
      coverage.value[resourceId] = data;
      return data;
    }
  }

  function resetCoverage(resourceId?: string) {
    if (!resourceId) return;
    const res = resourcesAll.value.find((l) => l.id === resourceId);
    if (!res) return;
    res.coverage = undefined;
  }

  function setResourcesActiveState(
    resourceIds?: string[],
    active: boolean = true,
    deactivateOthers: boolean = false
  ) {
    const targetResourceIds = !!resourceIds?.length
      ? resourceIds
      : resourcesAll.value.filter((r) => r.config.common.defaultActive).map((r) => r.id);
    resourcesAll.value = resourcesAll.value.map((r) => {
      if (targetResourceIds.includes(r.id)) {
        return {
          ...r,
          active: !!active,
        };
      } else if (deactivateOthers) {
        return {
          ...r,
          active: false,
        };
      }
      return r;
    });
  }

  return {
    all: resourcesAll,
    ofText: resourcesOfText,
    resourceTitles,
    getAggregations,
    applyContents,
    correctionsCount,
    correctionsCountTotal,
    corrections,
    loadCorrections,
    dataHash,
    error,
    loading,
    load,
    replace,
    add,
    remove,
    getCoverage,
    resetCoverage,
    setResourcesActiveState,
  };
});
