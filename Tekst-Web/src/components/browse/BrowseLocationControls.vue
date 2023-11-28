<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useStateStore, useBrowseStore } from '@/stores';
import { NButton, NModal, NSelect, NFormItem, NForm, NDivider } from 'naive-ui';
import type { NodeRead, TextRead } from '@/api';
import router from '@/router';
import ButtonFooter from '@/components/ButtonFooter.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { useMagicKeys, whenever } from '@vueuse/core';
import { GET } from '@/api';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';

import ArrowBackIosRound from '@vicons/material/ArrowBackIosRound';
import ArrowForwardIosRound from '@vicons/material/ArrowForwardIosRound';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';

const state = useStateStore();
const browse = useBrowseStore();
const route = useRoute();
const { message } = useMessages();

const { ArrowLeft, ArrowRight } = useMagicKeys();

const showModal = ref(false);
watch(showModal, (show) => show && initSelectModels());

const browseLevel = ref(state.text?.defaultLevel || 0);
const browseLevelOptions = computed(() =>
  state.textLevelLabels.map((l, i) => ({
    value: i,
    label: l,
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
  const { data: nodes, error } = await GET('/browse/nodes/{id}/path/options-by-root', {
    params: { path: { id: locationSelectModels.value[lvl].selected || '' } },
  });
  if (error) {
    message.error($t('errors.unexpected'), error);
    return;
  }
  // set nodes for all following levels
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > lvl) {
      // only do this if we're <= current browse level
      if (i <= browseLevel.value) {
        // set nodes
        lsm.nodes = nodes.shift() || [];
        // set selection
        lsm.selected = lsm.nodes[0]?.id || null;
        // set to no loading
      }
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
  const { data: nodesOptions, error } = await GET('/browse/nodes/{id}/path/options-by-head', {
    params: { path: { id: browse.nodePath[browseLevel.value]?.id } },
  });

  if (error) {
    message.error($t('errors.unexpected'), error);
    return;
  }
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
  const selectedLevel = locationSelectModels.value
    .reverse()
    .find((lsm) => !lsm.disabled && !!lsm.selected);
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

// initialize node path on mount
onMounted(() => browse.updateBrowseNodePath());

// react to keyboard for in-/decreasing location
whenever(ArrowRight, () => {
  router.push(getPrevNextRoute(1));
});
whenever(ArrowLeft, () => {
  router.push(getPrevNextRoute(-1));
});
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
        :disabled="browse.position === 0"
        :focusable="false"
        :title="$t('browse.toolbar.tipPreviousLocation')"
        size="large"
        color="#fff"
        @click="navigate"
      >
        <template #icon>
          <ArrowBackIosRound />
        </template>
      </n-button>
    </router-link>

    <n-button
      secondary
      :title="$t('browse.toolbar.tipSelectLocation')"
      :focusable="false"
      size="large"
      color="#fff"
      :disabled="!browse.nodePath[browseLevel]"
      @click="showModal = true"
    >
      <template #icon>
        <MenuBookOutlined />
      </template>
    </n-button>

    <router-link v-slot="{ navigate }" :to="getPrevNextRoute(1)" custom>
      <n-button
        secondary
        :focusable="false"
        :title="$t('browse.toolbar.tipNextLocation')"
        size="large"
        color="#fff"
        @click="navigate"
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
    :auto-focus="false"
    :closable="false"
    size="large"
    class="tekst-modal"
    to="#app-container"
  >
    <h2>
      {{ $t('browse.location.modalHeading') }}
      <HelpButtonWidget help-key="browseLocationControls" />
    </h2>
    <n-form
      label-placement="left"
      label-width="auto"
      :show-feedback="false"
      :show-require-mark="false"
    >
      <n-form-item :label="$t('browse.location.level')">
        <n-select v-model:value="browseLevel" :options="browseLevelOptions" />
      </n-form-item>

      <n-divider />

      <n-form-item
        v-for="(levelLoc, index) in locationSelectModels"
        :key="`${index}_loc_select`"
        :label="state.textLevelLabels[index]"
        class="location-select-item"
        :class="levelLoc.disabled && 'disabled'"
      >
        <n-select
          v-model:value="levelLoc.selected"
          :options="locationSelectOptions[index]"
          filterable
          placeholder="--"
          :loading="levelLoc.loading"
          :disabled="levelLoc.disabled || locationSelectOptions[index].length === 0"
          @update:value="() => updateSelectModelsFromLvl(index)"
        />
      </n-form-item>
    </n-form>
    <ButtonFooter>
      <n-button secondary :focusable="false" @click="showModal = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" @click="handleLocationSelect">
        {{ $t('general.selectAction') }}
      </n-button>
    </ButtonFooter>
  </n-modal>
</template>

<style scoped>
.text-location {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.location-select-item {
  margin-bottom: 0.5rem;
}

.location-select-item.disabled {
  opacity: 0.5;
}
</style>
