<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useStateStore, useBrowseStore } from '@/stores';
import { NButton, NModal, NSelect, NFormItem, NForm, NDivider } from 'naive-ui';
import ArrowBackIosRound from '@vicons/material/ArrowBackIosRound';
import ArrowForwardIosRound from '@vicons/material/ArrowForwardIosRound';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import { NodesApi, type NodeRead, type TextRead } from '@/openapi';
import router from '@/router';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';

const state = useStateStore();
const browse = useBrowseStore();
const route = useRoute();

const nodesApi = new NodesApi();

const showModal = ref(false);
watch(showModal, (show) => show && initSelectModels());

const browseLevel = ref(state.text?.defaultLevel || 0);
const browseLevelOptions = computed(() =>
  state.text?.levels.map((l: string, i: number) => ({
    label: l,
    value: i,
  }))
);
// sync browse level in location controls state with actual browse level (if possible)
watch(
  () => browse.level,
  (after) => (browseLevel.value = after !== undefined ? after : state.text?.defaultLevel || 0)
);
// react to browse level selection changes
watch(browseLevel, (after, before) => {
  if (showModal.value) {
    if (after > before) {
      updateSelectModelsFromLvl(before);
    }
    applyBrowseLevel();
  }
});

// model for location select inputs (local state)
interface LocationSelectModel {
  loading: boolean;
  selected: string | null;
  disabled: boolean;
  nodes: NodeRead[];
}
const locationSelectModels = ref<LocationSelectModel[]>(getEmptyModels());

// generate location select options from select model nodes
const locationSelectOptions = computed(() =>
  locationSelectModels.value.map((lsm) =>
    lsm.nodes.map((n) => ({
      label: n.label,
      value: n.id,
    }))
  )
);

// generate fresh location select models when text changes
watch(
  () => state.text,
  (after) => (locationSelectModels.value = getEmptyModels(after))
);

function getEmptyModels(text: TextRead | undefined = state.text): LocationSelectModel[] {
  if (!text) return [];
  return (
    text.levels.map((_, i) => ({
      loading: false,
      selected: null,
      nodes: [],
      options: [],
      disabled: i > browseLevel.value,
    })) || []
  );
}

async function updateSelectModelsFromLvl(lvl: number) {
  // abort if the highest enabled level was changed (nothing to do)
  if (lvl >= locationSelectModels.value.length - 1) {
    return;
  }
  // set loading state
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > lvl) {
      lsm.loading = true;
    }
  });
  // load node path options from node selected at lvl as root
  const nodes = await nodesApi
    .getPathOptionsByRootId({
      id: locationSelectModels.value[lvl].selected || '',
    })
    .then((response) => response.data);
  // set nodes for all following levels
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > lvl) {
      // set nodes
      lsm.nodes = nodes.shift() || [];
      // set selection
      lsm.selected = lsm.nodes[0].id || null;
      // set to no loading
      lsm.loading = false;
    }
  });
}

function applyBrowseLevel() {
  locationSelectModels.value.forEach((lsm, i) => {
    lsm.disabled = i > browseLevel.value;
    lsm.nodes = lsm.disabled ? [] : lsm.nodes;
    lsm.selected = lsm.disabled ? null : lsm.selected;
  });
}

async function initSelectModels() {
  // set all live models to loading
  locationSelectModels.value.forEach((lsm) => {
    lsm.loading = true;
  });

  // fetch nodes from head to root
  const nodesOptions = await nodesApi
    .getPathOptionsByHeadId({ id: browse.nodePath[browseLevel.value]?.id || '' })
    .then((response) => response.data);

  // apply browse level
  applyBrowseLevel();

  // manipulate each location select model
  let index = 0;
  for (const lsm of locationSelectModels.value) {
    // set options and selection
    if (index <= browseLevel.value) {
      // remember nodes for these options
      lsm.nodes = nodesOptions[index];
      // set selection
      lsm.selected = browse.nodePath[index]?.id || null;
    }
    index++;
    lsm.loading = false;
  }

  // locationSelectModels.value = models;
}

function getPrevNextRoute(step: number) {
  return {
    ...route,
    query: {
      ...route.query,
      pos: route.query.pos ? parseInt(route.query.pos.toString()) + step : 0,
    },
  };
}

function handleLocationSelect() {
  // we reverse the actual array here, but it will be created from scratch
  // anyway as soon as the location select modal opens again
  const selectedLevel = locationSelectModels.value.reverse().find((lsm) => !lsm.disabled);
  const selectedNode = selectedLevel?.nodes.find((n) => n.id === selectedLevel.selected);

  router.push({
    name: 'browse',
    params: { ...route.params },
    query: {
      ...route.query,
      lvl: selectedNode?.level,
      pos: selectedNode?.position,
    },
  });
  // close location select modal
  showModal.value = false;
}

onMounted(() => browse.updateBrowseNodePath());
</script>

<template>
  <!-- text location toolbar buttons -->
  <div class="text-location">
    <router-link
      v-slot="{
        // @ts-ignore
        navigate,
      }"
      :to="getPrevNextRoute(-1)"
      custom
    >
      <n-button
        secondary
        @click="navigate"
        :disabled="browse.position === 0"
        :focusable="false"
        :title="$t('browse.toolbar.tipPreviousLocation')"
        size="large"
        color="#fffe"
      >
        <template #icon>
          <ArrowBackIosRound />
        </template>
      </n-button>
    </router-link>

    <n-button
      secondary
      :title="$t('browse.toolbar.tipSelectLocation')"
      @click="showModal = true"
      :focusable="false"
      size="large"
      color="#fffe"
    >
      <template #icon>
        <MenuBookOutlined />
      </template>
    </n-button>

    <router-link v-slot="{ navigate }" :to="getPrevNextRoute(1)" custom>
      <n-button
        secondary
        @click="navigate"
        :focusable="false"
        :title="$t('browse.toolbar.tipNextLocation')"
        size="large"
        color="#fffe"
      >
        <template #icon>
          <ArrowForwardIosRound />
        </template>
      </n-button>
    </router-link>
  </div>

  <!-- text location selector modal -->
  <n-modal
    v-model:show="showModal"
    display-directive="if"
    preset="card"
    embedded
    :closable="false"
    size="large"
    class="textrig-modal"
  >
    <h2>{{ $t('browse.location.modalHeading') }}</h2>
    <n-form
      label-placement="left"
      label-width="auto"
      :show-feedback="false"
      :show-require-mark="false"
    >
      <n-form-item :label="$t('browse.location.level')">
        <n-select :options="browseLevelOptions" v-model:value="browseLevel" />
      </n-form-item>

      <n-divider />

      <n-form-item
        v-for="(levelLoc, index) in locationSelectModels"
        :label="state.text?.levels[index]"
        :key="`${index}_loc_select`"
        class="location-select-item"
        :class="levelLoc.disabled && 'disabled'"
      >
        <n-select
          v-model:value="levelLoc.selected"
          :options="locationSelectOptions[index]"
          filterable
          placeholder="--"
          :loading="levelLoc.loading"
          :disabled="levelLoc.disabled"
          @update:value="() => updateSelectModelsFromLvl(index)"
        />
      </n-form-item>
    </n-form>
    <!-- <pre style="font-size: 11px; line-height: 1">{{ locationSelectModels }}</pre> -->
    <ModalButtonFooter>
      <n-button @click="showModal = false" :focusable="false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" @click="handleLocationSelect">
        {{ $t('general.selectAction') }}
      </n-button>
    </ModalButtonFooter>
  </n-modal>
</template>

<style scoped>
.text-location {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}
.location-select-item {
  margin-bottom: 0.5rem;
}
.location-select-item.disabled {
  opacity: 0.5;
}
</style>
