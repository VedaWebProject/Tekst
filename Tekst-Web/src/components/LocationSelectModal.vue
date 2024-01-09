<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useStateStore } from '@/stores';
import { NButton, NModal, NSelect, NFormItem, NForm, NDivider } from 'naive-ui';
import type { NodeRead, TextRead } from '@/api';
import ButtonShelf from '@/components/ButtonShelf.vue';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import { GET } from '@/api';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';

import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import IconHeading from '@/components/typography/IconHeading.vue';

const props = withDefaults(
  defineProps<{
    nodePath: NodeRead[];
    showLevelSelect?: boolean;
    show?: boolean;
  }>(),
  {
    showLevelSelect: true,
    show: false,
  }
);

const emit = defineEmits(['update:show', 'update:nodePath']);

const state = useStateStore();
const { message } = useMessages();

watch(
  () => props.show,
  (show) => show && initSelectModels()
);

const locationLevel = ref(props.nodePath.length - 1);
const locationLevelOptions = computed(() =>
  state.textLevelLabels.map((l, i) => ({
    value: i,
    label: l,
  }))
);
// sync browse level in location controls state with actual browse level (if possible)
watch(
  () => props.nodePath.length,
  (after) => {
    locationLevel.value = after - 1;
  }
);
// react to browse level selection changes
watch(locationLevel, (after, before) => {
  if (props.show) {
    if (after > before) {
      updateSelectModelsFromLvl(before);
    }
    applyBrowseLevel();
  }
});

// interface for location select options (local state)
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
      disabled: props.showLevelSelect && i > locationLevel.value,
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
      if (i <= locationLevel.value) {
        // set nodes
        lsm.nodes = nodes.shift() || [];
        // set selection
        lsm.selected = lsm.nodes[0]?.id || null;
      }
      // set to no loading
      lsm.loading = false;
    }
  });
}

function applyBrowseLevel() {
  locationSelectModels.value.forEach((lsm, i) => {
    lsm.disabled = props.showLevelSelect && i > locationLevel.value;
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
    params: { path: { id: props.nodePath[locationLevel.value].id ?? '' } },
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
    if (index <= locationLevel.value) {
      // remember nodes for these options
      lsm.nodes = nodesOptions[index];
      // set selection
      lsm.selected = props.nodePath?.[index]?.id || null;
    }
    index++;
    lsm.loading = false;
  }
}

function handleLocationSelect() {
  // emit selected node path
  emit(
    'update:nodePath',
    locationSelectModels.value
      .filter((_, i) => i <= locationLevel.value)
      .map((lsm) => lsm.nodes.find((n) => n.id === lsm.selected))
  );
  emit('update:show', false);
  // // we reverse the actual array here, but it will be created from scratch
  // // anyway as soon as the location select modal opens again
  // const selectedLevel = locationSelectModels.value
  //   .reverse()
  //   .find((lsm) => !lsm.disabled && !!lsm.selected);
  // const selectedNode = selectedLevel?.nodes.find((n) => n.id === selectedLevel.selected);

  // router.push({
  //   name: 'browse',
  //   params: { ...route.params },
  //   query: {
  //     ...route.query,
  //     lvl: selectedNode?.level,
  //     pos: selectedNode?.position,
  //   },
  // });
}
</script>

<template>
  <n-modal
    :show="show"
    display-directive="if"
    preset="card"
    embedded
    :auto-focus="false"
    header-style="padding-bottom: 1.5rem"
    class="tekst-modal"
    to="#app-container"
    @update:show="emit('update:show', $event)"
    @mask-click="emit('update:show', false)"
  >
    <template #header>
      <IconHeading level="2" :icon="MenuBookOutlined" style="margin: 0">
        {{ $t('browse.location.modalHeading') }}
        <HelpButtonWidget help-key="browseLocationControls" />
      </IconHeading>
    </template>

    <n-form
      label-placement="left"
      label-width="auto"
      :show-feedback="false"
      :show-require-mark="false"
    >
      <template v-if="showLevelSelect">
        <n-form-item :label="$t('browse.location.level')">
          <n-select v-model:value="locationLevel" :options="locationLevelOptions" />
        </n-form-item>

        <n-divider />
      </template>

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
          placeholder="–"
          :loading="levelLoc.loading"
          :disabled="
            levelLoc.loading || levelLoc.disabled || locationSelectOptions[index].length === 0
          "
          @update:value="() => updateSelectModelsFromLvl(index)"
        />
      </n-form-item>
    </n-form>
    <ButtonShelf top-gap>
      <n-button secondary :focusable="false" @click="emit('update:show', false)">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" @click="handleLocationSelect">
        {{ $t('general.selectAction') }}
      </n-button>
    </ButtonShelf>
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
