import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore } from '@/stores';
import type { NodeRead } from '@/openapi';
import { NodesApi } from '@/openapi/api';

export const useBrowseStore = defineStore('browse', () => {
  // define resources
  const state = useStateStore();
  const route = useRoute();
  const router = useRouter();
  const nodesApi = new NodesApi();

  // browse node path
  const nodePath = ref<NodeRead[]>([]);
  const nodePathHead = computed(() =>
    nodePath.value.length > 0 ? nodePath.value[nodePath.value.length - 1] : undefined
  );
  const nodePathRoot = computed(() => (nodePath.value.length > 0 ? nodePath.value[0] : undefined));
  const level = computed(() => nodePathHead.value?.level);
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
          resetBrowseLocation();
        }
      } else {
        resetBrowseLocation();
      }
    }
  }

  // reset browse location
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

  return {
    nodePath,
    nodePathHead,
    nodePathRoot,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
  };
});
