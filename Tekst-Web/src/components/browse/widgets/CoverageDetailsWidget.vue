<script setup lang="ts">
import { NButton } from 'naive-ui';
import ButtonShelf from '@/components/ButtonShelf.vue';
import { ref } from 'vue';
import {
  GET,
  type AnyResourceRead,
  type ResourceCoverage,
  type ResourceCoverageDetails,
} from '@/api';
import { watch } from 'vue';
import { RouterLink } from 'vue-router';
import { useRoute } from 'vue-router';
import IconHeading from '@/components/typography/IconHeading.vue';

import PercentOutlined from '@vicons/material/PercentOutlined';
import { useStateStore } from '@/stores';
import GenericModal from '@/components/GenericModal.vue';

const props = defineProps<{
  resource: AnyResourceRead;
  coverageBasic?: ResourceCoverage;
  show?: boolean;
}>();

const emit = defineEmits(['update:show', 'navigated']);

const state = useStateStore();
const route = useRoute();

const coverageDetails = ref<ResourceCoverageDetails>();
const loading = ref(false);
const error = ref(false);

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

function handleNodeClick() {
  emit('update:show', false);
  emit('navigated');
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
      <IconHeading level="2" :icon="PercentOutlined" style="margin: 0">
        {{ resource.title }}:
        {{ $t('browse.units.widgets.infoWidget.coverage') }}
      </IconHeading>
    </template>

    <p v-if="coverageBasic">
      {{
        $t('browse.units.widgets.infoWidget.coverageStatement', {
          present: coverageBasic.covered,
          total: coverageBasic.total,
          level: state.textLevelLabels[resource.level],
        })
      }}
    </p>

    <p v-if="error">
      {{ $t('errors.unexpected') }}
    </p>

    <p v-else-if="loading">
      {{ $t('general.loading') }}
    </p>

    <div v-else style="margin: var(--layout-gap) 0">
      <div v-for="(nodesBlock, index) in coverageDetails?.nodesCoverage" :key="`block-${index}`">
        <h3 v-if="coverageDetails?.parentLabels[index]" style="margin-bottom: 0.5rem">
          {{ state.textLevelLabels[resource.level - 1] }}:
          {{ coverageDetails?.parentLabels[index] }}
        </h3>
        <div class="cov-block">
          <router-link
            v-for="node in nodesBlock"
            :key="node.position"
            :to="{
              name: 'browse',
              params: { text: route.params.text },
              query: {
                lvl: resource.level,
                pos: node.position,
              },
            }"
            :title="`${state.textLevelLabels[resource.level]}: ${node.label}`"
            @click="handleNodeClick"
          >
            <div class="cov-box" :class="node.covered && 'covered'"></div>
          </router-link>
        </div>
      </div>
    </div>

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
  background-color: var(--main-bg-color);
  border-radius: 2px;
  opacity: 0.75;
  transition: 0.2s;
}
.cov-box:hover {
  opacity: 1;
}

.cov-box.covered {
  background-color: var(--accent-color);
}
</style>
