<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStateStore } from '@/stores';
import { NButton, NModal, NSelect, NFormItem, NForm, NDivider } from 'naive-ui';
import ArrowBackIosRound from '@vicons/material/ArrowBackIosRound';
import ArrowForwardIosRound from '@vicons/material/ArrowForwardIosRound';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import { NodesApi } from '@/openapi';

const state = useStateStore();
const route = useRoute();
const router = useRouter();

const nodesApi = new NodesApi();

const showLocationSelectModal = ref(false);
const browseLevel = ref(state.text?.defaultLevel || 0);
const browseLevelOptions = computed(() =>
  state.text?.levels.map((l: string, i: number) => ({
    label: l,
    value: i,
  }))
);

// model for location select inputs (local state)
interface LocationSelectModel {
  loading: boolean;
  selected?: string;
  disabled?: boolean;
  options?: { label: string; value: string }[];
}
const locationSelectModels = ref<LocationSelectModel[]>(getRawLocationSelectModels());

function getRawLocationSelectModels(): LocationSelectModel[] {
  return (
    state.text?.levels.map((_, i) => ({
      loading: false,
      disabled: i > browseLevel.value,
    })) || []
  );
}

function handleBrowseLevelUpdate() {
  locationSelectModels.value.forEach((lsm: LocationSelectModel, i: number) => {
    lsm.loading = false;
    lsm.disabled = i > browseLevel.value;
    lsm.selected = lsm.disabled ? undefined : lsm.selected;
    lsm.options = lsm.disabled ? [] : lsm.options;
  });
}

watch(showLocationSelectModal, (show) => {
  if (show) {
    browseLevel.value = state.browseNode?.level || state.text?.defaultLevel || 0;
    handleBrowseLevelUpdate();
  } else {
    // ... or else what?!
  }
});

async function updateLocationSelectModels(changedLevel: number) {
  // TODO implement!
  console.log('updateLocationSelectModels LVL', changedLevel);
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

function resetBrowseLocation(level: number = state.browseNode?.level || 0, position: number = 0) {
  router.replace({
    ...route,
    query: {
      ...route.query,
      lvl: level,
      pos: position,
    },
  });
}

async function updateBrowseNodeByURI() {
  if (route.name === 'browse') {
    const qLvl = parseInt(route.query.lvl?.toString() || '') ?? 0;
    const qPos = parseInt(route.query.pos?.toString() || '') ?? 0;
    if (Number.isInteger(qLvl) && Number.isInteger(qPos)) {
      try {
        const node = await nodesApi
          .findNodes({
            textId: state.text?.id || '',
            level: qLvl,
            position: qPos,
          })
          .then((response) => response.data[0]);
        if (!node) throw new Error();
        state.browseNode = node;
        browseLevel.value = node.level;
        locationSelectModels.value = getRawLocationSelectModels();
        updateLocationSelectModels(0);
      } catch {
        resetBrowseLocation();
      }
    } else {
      resetBrowseLocation();
    }
  }
}

onMounted(() => updateBrowseNodeByURI());
watch(route, (after) => after.name === 'browse' && updateBrowseNodeByURI());
</script>

<template>
  <!-- text location toolbar buttons -->
  <div class="text-location">
    <router-link v-slot="{ navigate }" :to="getPrevNextRoute(-1)" custom>
      <n-button
        secondary
        @click="navigate"
        :disabled="state.browseNode?.position === 0"
        :focusable="false"
        title="Previous location"
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
      title="Select location"
      @click="showLocationSelectModal = true"
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
        title="Next location"
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
    v-model:show="showLocationSelectModal"
    display-directive="if"
    preset="card"
    embedded
    :closable="false"
    size="huge"
    style="width: 600px; max-width: 95%"
  >
    <h2>Select location</h2>
    <n-form
      label-placement="left"
      label-width="auto"
      size="large"
      :show-feedback="false"
      :show-require-mark="false"
    >
      <n-form-item label="Level">
        <n-select
          :options="browseLevelOptions"
          v-model:value="browseLevel"
          @update:value="handleBrowseLevelUpdate"
        />
      </n-form-item>

      <n-divider />

      <n-form-item
        v-for="(levelLoc, index) in locationSelectModels"
        :label="state.text?.levels[index]"
        :key="`${index}_${state.browseNode?.label}`"
        class="location-select-item"
        :class="levelLoc.disabled && 'disabled'"
      >
        <n-select
          v-model:value="levelLoc.selected"
          :options="levelLoc.options"
          filterable
          :placeholder="levelLoc.disabled ? '--' : state.text?.levels[index]"
          :loading="levelLoc.loading && !levelLoc.disabled"
          :disabled="levelLoc.disabled"
          @update:value="() => updateLocationSelectModels(index)"
        />
      </n-form-item>
    </n-form>
    <pre style="font-size: 11px; line-height: 1">{{ locationSelectModels }}</pre>
    <div style="text-align: right">
      <n-button type="primary">Select</n-button>
    </div>
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
