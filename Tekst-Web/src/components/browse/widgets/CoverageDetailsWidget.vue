<script setup lang="ts">
import {
  NThing,
  NIcon,
  NEllipsis,
  NSpin,
  NButton,
  NVirtualList,
  type VirtualListInst,
} from 'naive-ui';
import ButtonShelf from '@/components/ButtonShelf.vue';
import { computed, ref } from 'vue';
import {
  GET,
  type AnyResourceRead,
  type ResourceCoverage,
  type ResourceCoverageDetails,
} from '@/api';
import { watch } from 'vue';
import { useRoute } from 'vue-router';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useStateStore } from '@/stores';
import GenericModal from '@/components/GenericModal.vue';
import router from '@/router';

import PercentOutlined from '@vicons/material/PercentOutlined';
import VerticalAlignTopOutlined from '@vicons/material/VerticalAlignTopOutlined';
import VerticalAlignBottomOutlined from '@vicons/material/VerticalAlignBottomOutlined';

const props = defineProps<{
  resource: AnyResourceRead;
  coverageBasic?: ResourceCoverage;
  show?: boolean;
}>();

const emit = defineEmits(['update:show', 'navigated']);

const state = useStateStore();
const route = useRoute();

const coverageDetails = ref<ResourceCoverageDetails>();
const coverageListItems = computed(
  () =>
    coverageDetails.value?.nodesCoverage.map((nodes, i) => ({
      title: `${state.textLevelLabels[props.resource.level - 1]}: ${coverageDetails.value
        ?.parentLabels[i]}`,
      extra: `${nodes.filter((n) => n.covered).length}/${nodes.length}`,
      nodes: nodes,
    }))
);

const loading = ref(false);
const error = ref(false);
const virtualListInst = ref<VirtualListInst>();

async function handleEnter() {
  loading.value = true;
  const { data, error: e } = await GET('/browse/resources/{id}/coverage-details', {
    params: { path: { id: props.resource.id } },
  });
  if (!e) {
    coverageDetails.value = data;
  } else {
    error.value = true;
  }
  loading.value = false;
}

function handleLeave() {
  loading.value = false;
  error.value = false;
  coverageDetails.value = undefined;
}

function handleNodeClick(level: number, position: number) {
  router.push({
    name: 'browse',
    params: { text: route.params.text },
    query: {
      lvl: level,
      pos: position,
    },
  });
  emit('update:show', false);
  emit('navigated');
}

function handleScrollClick(scrollType: 'up' | 'down' | 'top' | 'bottom') {
  const index = {
    up: 0,
    down: 0,
    top: 0,
    bottom: (coverageListItems.value?.length || 1) - 1,
  }[scrollType];
  virtualListInst.value?.scrollTo({ index: index, behavior: 'smooth', debounce: true });
}

watch(
  () => props.show,
  (after) => after && handleEnter()
);
</script>

<template>
  <GenericModal
    :show="show"
    width="wide"
    @close="$emit('update:show', false)"
    @mask-click="$emit('update:show', false)"
    @after-leave="handleLeave"
  >
    <template #header>
      <IconHeading level="2" :icon="PercentOutlined" style="margin: 0" ellipsis>
        {{ resource.title }}:
        {{ $t('browse.units.widgets.infoWidget.coverage') }}
      </IconHeading>
    </template>

    <p v-if="error">
      {{ $t('errors.unexpected') }}
    </p>

    <n-spin
      v-else-if="loading"
      :description="$t('general.loading')"
      style="width: 100%; display: flex; justify-content: center; margin: 2rem 0"
    />

    <template v-else-if="coverageListItems?.length">
      <div style="display: flex; justify-content: space-between">
        <template v-if="coverageBasic">
          <n-ellipsis>
            {{
              $t('browse.units.widgets.infoWidget.coverageStatement', {
                present: coverageBasic.covered,
                total: coverageBasic.total,
                level: state.textLevelLabels[resource.level],
              })
            }}
          </n-ellipsis>
        </template>
        <ButtonShelf bottom-gap wrap="nowrap" group-wrap="nowrap">
          <n-button secondary size="small" :focusable="false" @click="handleScrollClick('top')">
            <template #icon>
              <n-icon :component="VerticalAlignTopOutlined" />
            </template>
          </n-button>
          <n-button secondary size="small" :focusable="false" @click="handleScrollClick('bottom')">
            <template #icon>
              <n-icon :component="VerticalAlignBottomOutlined" />
            </template>
          </n-button>
        </ButtonShelf>
      </div>

      <n-virtual-list
        ref="virtualListInst"
        style="max-height: calc(100vh - 300px)"
        :item-size="42"
        :items="coverageListItems"
        item-resizable
      >
        <template #default="{ item }">
          <n-thing>
            <template #header>
              <span style="font-weight: var(--app-ui-font-weight-light)">{{ item.title }}</span>
            </template>
            <template #header-extra>
              <span
                style="
                  font-weight: var(--app-ui-font-weight-light);
                  margin-right: var(--layout-gap);
                "
              >
                ({{ item.extra }})
              </span>
            </template>
            <template #description>
              <div class="cov-block">
                <div
                  v-for="node in item.nodes"
                  :key="node.position"
                  class="cov-box"
                  :class="node.covered && 'covered'"
                  :title="`${state.textLevelLabels[resource.level]}: ${node.label}`"
                  @click="() => handleNodeClick(resource.level, node.position)"
                ></div>
              </div>
            </template>
          </n-thing>
        </template>
      </n-virtual-list>
    </template>

    <ButtonShelf top-gap>
      <n-button type="primary" @click="$emit('update:show', false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
</template>

<style scoped>
.cov-block {
  margin: 0.25rem 0 0.75rem 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.cov-box {
  width: 16px;
  height: 16px;
  background-color: var(--col-error);
  border-radius: 2px;
  opacity: 0.75;
  transition: 0.2s;
  cursor: pointer;
}
.cov-box:hover {
  opacity: 1;
}

.cov-box.covered {
  background-color: var(--col-success);
}
</style>
