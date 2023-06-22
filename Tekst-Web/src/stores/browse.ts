import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore, useAuthStore } from '@/stores';
import type { NodeRead } from '@/openapi';
import type { AxiosResponse } from 'axios';
import { useApi } from '@/api';
import { useMessages } from '@/messages';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const auth = useAuthStore();
  const route = useRoute();
  const router = useRouter();
  const { message } = useMessages();

  // API clients
  const { nodesApi } = useApi();
  const { layersApi } = useApi();
  const { unitsApi } = useApi();

  /* BASIC BROWSE UI STATE */

  const showLayerToggleDrawer = ref(false);
  const reducedView = ref(false);
  const loading = ref(true); // this is intentional!

  /* BROWSE NODE PATH */

  const nodePath = ref<NodeRead[]>([]);
  const nodePathHead = computed(() =>
    nodePath.value.length > 0 ? nodePath.value[nodePath.value.length - 1] : undefined
  );
  const nodePathRoot = computed(() => (nodePath.value.length > 0 ? nodePath.value[0] : undefined));
  const level = computed(() =>
    nodePathHead.value?.level !== undefined
      ? nodePathHead.value.level
      : state.text?.defaultLevel || 0
  );
  const position = computed(() => nodePathHead.value?.position);

  // update browse node path
  async function updateBrowseNodePath(lvl?: string, pos?: string) {
    if (route.name !== 'browse') return;
    const qLvl = parseInt(lvl || route.query.lvl?.toString() || '') ?? 0;
    const qPos = parseInt(pos || route.query.pos?.toString() || '') ?? 0;
    if (Number.isInteger(qLvl) && Number.isInteger(qPos)) {
      try {
        // fill browse node path up to root (no more parent)
        const path = await nodesApi
          .getPathByHeadLocation({
            textId: state.text?.id || '',
            level: qLvl,
            position: qPos,
          })
          .then((response) => response.data);
        if (!path || path.length == 0) {
          throw new Error();
        }
        nodePath.value = path;
      } catch {
        resetBrowseLocation(level.value);
      }
    } else {
      resetBrowseLocation();
    }
  }

  // reset browse location (change URI parameters)
  function resetBrowseLocation(
    level: number = state.text?.defaultLevel || 0,
    position: number = 0,
    text: string = state.fallbackText?.slug || ''
  ) {
    router.replace({
      ...route,
      params: {
        text: text,
      },
      query: {
        ...route.query,
        lvl: level,
        pos: position,
      },
    });
  }

  // set browse location to text default when text changes
  watch(
    () => state.text,
    () => {
      route.name === 'browse' && resetBrowseLocation();
      nodePath.value = [];
    }
  );

  // react to route changes concerning browse state
  watch([() => route.query.lvl, () => route.query.pos], ([newLvl, newPos]) => {
    if (route.name === 'browse') {
      updateBrowseNodePath(newLvl?.toString(), newPos?.toString());
    }
  });

  /* BROWSE LAYERS AND UNITS */

  const layers = ref<Record<string, any>[]>([]);

  async function loadLayersData() {
    if (!state.text) return;
    // set to loading
    loading.value = true;
    // fetch data
    try {
      // fetch layers data
      const layersData = await layersApi
        .findLayers({ textId: state.text.id })
        .then((response: AxiosResponse) => response.data);
      layersData.forEach((l: Record<string, any>) => {
        // keep layer deactivated if it was before
        const existingLayer = layers.value.find((lo) => lo.id === l.id);
        l.active = !existingLayer || existingLayer.active;
      });
      loadUnitsData(layersData);
    } catch (e) {
      // console.error(e);
      message.error('Error loading data layers for this location');
      loading.value = false;
    }
  }

  async function loadUnitsData(layersData = layers.value) {
    if (!nodePathHead.value) {
      layers.value = [];
      loading.value = false;
      return;
    }
    // set to loading
    loading.value = true;
    try {
      // fetch units data
      const unitsData = await unitsApi
        .findUnits({ nodeId: nodePath.value.map((n) => n.id) })
        .then((response: AxiosResponse) => response.data);
      // assign units to layers
      layersData.forEach((l: Record<string, any>) => {
        l.units = unitsData.filter((u: Record<string, any>) => u.layerId == l.id);
      });
      // assign (potentially) fresh layers/untis data to store prop
      layers.value = layersData;
    } catch (e) {
      // console.error(e);
      message.error('Error loading data layer units for this location');
    } finally {
      loading.value = false;
    }
  }

  // load layers/units data on browse location change
  watch(
    () => nodePathHead.value,
    (after: NodeRead | undefined, before: NodeRead | undefined) => {
      if (after?.textId === before?.textId && layers.value.length > 0) {
        // selected text didn't change, only the location did,
        // so it's enough to load new units data (secial case: if the layers
        // array is empty, we try to load layers again,
        // as the user might have just logged out)
        loadUnitsData();
      } else {
        // node path head changed because a different text was selected,
        // so we have to load full layers data AND according units data
        loadLayersData();
      }
    }
  );

  // remove accessed data that might be restricted
  watch(
    () => auth.user,
    (after, before) => {
      if (before && !after) layers.value = [];
    }
  );

  return {
    showLayerToggleDrawer,
    reducedView,
    loading,
    layers,
    nodePath,
    nodePathHead,
    nodePathRoot,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
    loadLayersData,
  };
});
