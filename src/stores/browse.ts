import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useMessagesStore, useStateStore } from '@/stores';
import type { NodeRead } from '@/openapi';
import { LayersApi, NodesApi, UnitsApi } from '@/openapi/api';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const route = useRoute();
  const router = useRouter();
  const messages = useMessagesStore();

  // API clients
  const nodesApi = new NodesApi();
  const layersApi = new LayersApi();
  const unitsApi = new UnitsApi();

  /* BROWSE UI CONTROLS */

  const showLayerToggleDrawer = ref(false);

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
  async function updateBrowseNodePath() {
    if (route.name === 'browse') {
      const qLvl = parseInt(route.query.lvl?.toString() || '') ?? 0;
      const qPos = parseInt(route.query.pos?.toString() || '') ?? 0;
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
  }

  // reset browse location (change URI parameters)
  function resetBrowseLocation(
    level: number = state.text?.defaultLevel || 0,
    position: number = 0
  ) {
    router.replace({
      ...route,
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
    () => resetBrowseLocation()
  );

  // react to route changes concerning browse state
  watch(route, (after, before) => {
    if (
      after.name === 'browse' &&
      before.name === 'browse' &&
      after.params.text === before.params.text
    ) {
      updateBrowseNodePath();
    }
  });

  /* BROWSE LAYERS AND UNITS */

  const layers = ref<Record<string, Record<string, any>>>({});
  const units = ref<Record<string, Record<string, any>>>({});

  // load layers
  async function loadLayersData() {
    if (!state.text) return;
    Object.keys(units.value).forEach((unitId) => (units.value[unitId].loading = true));
    try {
      const data = await layersApi
        .findLayers({ textId: state.text.id })
        .then((response) => response.data);
      const layersData: Record<string, any> = {};
      data.forEach((l: Record<string, any>) => {
        layersData[l.id] = {
          ...l,
          active: true, // TODO: when is a layer active by default?
        };
      });
      layers.value = layersData;
    } catch (e) {
      console.error(e);
      messages.error('Error loading data layers for this location');
    }
    loadUnitsData();
  }

  // load units
  async function loadUnitsData() {
    if (!nodePathHead.value) return;
    try {
      const data = await unitsApi
        .findUnits({ nodeId: [nodePathHead.value.id] })
        .then((response) => response.data);
      const unitsData: Record<string, any> = {};
      data.forEach((u: Record<string, any>) => {
        // get layer this unit belongs to to add some of its data
        const l = layers.value[u.layerId];
        unitsData[u.id] = {
          ...u,
          layerType: l?.layerType,
          layerTitle: l?.title,
          loading: false,
        };
      });
      units.value = unitsData;
    } catch (e) {
      console.error(e);
      messages.error('Error loading data layer units for this location');
    }
  }

  // load layers data on text change
  watch(
    () => state.text,
    () => {
      route.name === 'browse' && loadLayersData();
    }
  );

  // load layers data on browse location change
  watch(
    () => nodePathHead.value,
    () => loadUnitsData()
  );

  return {
    showLayerToggleDrawer,
    layers,
    units,
    nodePath,
    nodePathHead,
    nodePathRoot,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
    loadUnitsData,
    loadLayersData,
  };
});
