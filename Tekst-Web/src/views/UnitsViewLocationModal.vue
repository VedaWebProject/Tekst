<script setup lang="ts">
import { NForm, NButton, NModal, NFormItem, NSelect } from 'naive-ui';
import { type NodeRead, GET } from '@/api';
import { ref } from 'vue';
import { computed, watch } from 'vue';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useMessages } from '@/messages';
import { useRoute, useRouter } from 'vue-router';
import ButtonFooter from '@/components/ButtonFooter.vue';

import MenuBookOutlined from '@vicons/material/MenuBookOutlined';

const props = defineProps<{
  nodePath?: NodeRead[];
  level: number;
  show?: boolean;
}>();
const emit = defineEmits(['update:show', 'submit']);

const state = useStateStore();
const { message } = useMessages();
const router = useRouter();
const route = useRoute();

watch(
  () => props.show,
  (show) => show && initSelectModels()
);
const node = computed<NodeRead | undefined>(() => props.nodePath?.[props.level]);

// interface for location select options (local state)
interface LocationSelectModel {
  loading: boolean;
  selected: string | null;
  nodes: NodeRead[];
}
const locationSelectModels = ref<LocationSelectModel[]>(getEmptyLocationSelectModels());
// generate location select options from select model nodes
const locationSelectOptions = computed(() =>
  locationSelectModels.value.map((lsm) =>
    lsm.nodes.map((n) => ({
      label: n.label,
      value: n.id,
    }))
  )
);

function getEmptyLocationSelectModels(): LocationSelectModel[] {
  if (!props.nodePath) return [];
  return (
    props.nodePath.map(() => ({
      loading: false,
      selected: null,
      nodes: [],
      options: [],
    })) || []
  );
}

async function updateSelectModelsFromLvl(lvl: number) {
  if (!node.value) return;
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
      // only do this if we're <= current level
      if (i <= (node.value?.level || 0)) {
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

function handleLocationSelect() {
  // we reverse the actual array here, but it will be created from scratch
  // anyway as soon as the location select modal opens again
  const selectedLevel = locationSelectModels.value.reverse()[0];
  const selectedNode = selectedLevel.nodes.find((n) => n.id === selectedLevel.selected);

  router.push({
    name: 'resourceUnits',
    params: { ...route.params, pos: selectedNode?.position },
  });
  emit('submit', selectedNode?.position || 0);
  emit('update:show', false);
}

async function initSelectModels() {
  locationSelectModels.value = getEmptyLocationSelectModels();
  // set all live models to loading
  locationSelectModels.value.forEach((lsm) => {
    lsm.loading = true;
  });

  // fetch nodes from head to root
  const { data: nodesOptions, error } = await GET('/browse/nodes/{id}/path/options-by-head', {
    params: { path: { id: node.value?.id || '' } },
  });

  if (error) {
    message.error($t('errors.unexpected'), error);
    return;
  }

  // manipulate each location select model
  let index = 0;
  for (const lsm of locationSelectModels.value) {
    // set options and selection
    if (index <= (node.value?.level || 0)) {
      // remember nodes for these options
      lsm.nodes = nodesOptions[index];
      // set selection
      lsm.selected = props.nodePath?.[index]?.id || null;
    }
    index++;
    lsm.loading = false;
  }
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
    size="large"
    class="tekst-modal"
    to="#app-container"
    @update:show="emit('update:show', $event)"
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
      <n-form-item
        v-for="(levelLoc, index) in locationSelectModels"
        :key="`${index}_loc_select`"
        :label="state.textLevelLabels[index]"
        class="location-select-item"
      >
        <n-select
          v-model:value="levelLoc.selected"
          :options="locationSelectOptions[index]"
          filterable
          placeholder="–"
          :loading="levelLoc.loading"
          :disabled="levelLoc.loading || locationSelectOptions[index].length === 0"
          @update:value="() => updateSelectModelsFromLvl(index)"
        />
      </n-form-item>
    </n-form>
    <ButtonFooter>
      <n-button secondary :focusable="false" @click="emit('update:show', false)">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" @click="handleLocationSelect">
        {{ $t('general.selectAction') }}
      </n-button>
    </ButtonFooter>
  </n-modal>
</template>
