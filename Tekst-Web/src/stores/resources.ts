import {
  GET,
  type AnyContentRead,
  type AnyResourceRead,
  type CorrectionRead,
  type KeyValueAggregations,
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
  const aggregations = ref<Record<string, KeyValueAggregations>>({});
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

  function processResources(resources: AnyResourceRead[]) {
    return (
      resources
        // sort resources by configured sort order
        .sort((a, b) => (a.config.general.sortOrder ?? 0) - (b.config.general.sortOrder ?? 0))
        // add additional props for quick use throughout the client
        .map((r) => {
          const existingResource = resourcesAll.value.find((re) => re.id === r.id);
          return {
            ...r,
            active: !!existingResource?.active || !!r.config.general.defaultActive,
            contents: existingResource?.contents ?? [],
            contentFont: [r.config.general.font, state.pf?.state.contentFont, 'serif']
              .filter((f) => !!f)
              .join(', '),
          };
        })
    );
  }

  async function load() {
    if (loading.value) {
      return;
    }
    loading.value = true;
    error.value = false;

    const { data, error: err } = await GET('/resources'); // fetch ALL resources

    if (!err) {
      resourcesAll.value = processResources(data);
    } else {
      error.value = true;
    }
    corrections.value = {};
    loading.value = false;
  }

  function addCorrection(resourceId: string, correction: CorrectionRead) {
    corrections.value[resourceId] = corrections.value[resourceId] ?? [];
    corrections.value[resourceId].unshift(correction);
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
      resourcesAll.value = processResources(
        resourcesAll.value.map((r) =>
          r.id === resource.id ? { ...resource, active: r.active, contents: r.contents } : r
        )
      );
    } else {
      add(resource);
    }
  }

  function add(resource: AnyResourceRead) {
    resource.active = resource.config.general.defaultActive;
    resourcesAll.value = processResources(resourcesAll.value.concat([resource]));
  }

  function remove(resourceId: string) {
    resourcesAll.value = resourcesAll.value.filter((r) => r.id !== resourceId);
  }

  async function getAggregations(resourceId: string): Promise<KeyValueAggregations> {
    if (!resourcesAll.value.find((r) => r.id === resourceId)) return [];
    const agg = aggregations.value[resourceId];
    if (agg) return agg;
    const { data, error } = await GET('/resources/{id}/aggregations', {
      params: { path: { id: resourceId } },
    });
    if (!error && !!data) {
      aggregations.value[resourceId] = data as KeyValueAggregations;
      return data as KeyValueAggregations;
    } else {
      aggregations.value[resourceId] = [];
      return [];
    }
  }

  function applyContents(contents: AnyContentRead[]) {
    resourcesAll.value.forEach((r) => {
      r.contents = contents.filter((c) => c.resourceId === r.id);
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
      : resourcesAll.value.filter((r) => r.config.general.defaultActive).map((r) => r.id);
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
    addCorrection,
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
