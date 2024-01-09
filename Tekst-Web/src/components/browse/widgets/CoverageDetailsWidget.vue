<script setup lang="ts">
import { NButton, NModal } from 'naive-ui';
import ButtonShelf from '@/components/ButtonShelf.vue';
import { ref } from 'vue';
import { GET, type AnyResourceRead, type ResourceNodeCoverage, type ResourceCoverage } from '@/api';
import { watch } from 'vue';
import { RouterLink } from 'vue-router';
import { useRoute } from 'vue-router';
import IconHeading from '@/components/typography/IconHeading.vue';

import PercentOutlined from '@vicons/material/PercentOutlined';
import { useStateStore } from '@/stores';

const props = defineProps<{
  resource: AnyResourceRead;
  coverageBasic?: ResourceCoverage;
  show?: boolean;
}>();

const emit = defineEmits(['update:show', 'navigated']);

const state = useStateStore();
const route = useRoute();

const coverageData = ref<ResourceNodeCoverage[][]>();
const loading = ref(false);
const error = ref(false);

async function handleEnter() {
  loading.value = true;
  const { data, error: e } = await GET('/browse/resources/{id}/coverage-details', {
    params: { path: { id: props.resource.id } },
  });
  if (!e) {
    coverageData.value = data;
  } else {
    error.value = true;
  }
  loading.value = false;
}

function handleLeave() {
  loading.value = false;
  error.value = false;
  coverageData.value = undefined;
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
  <n-modal
    :show="show"
    display-directive="if"
    preset="card"
    class="tekst-modal-wide"
    :bordered="false"
    :auto-focus="false"
    :closable="true"
    header-style="padding-bottom: .25rem"
    to="#app-container"
    embedded
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
      <div v-for="(nodesBlock, index) in coverageData" :key="`block-${index}`" class="cov-block">
        <router-link
          v-for="node in nodesBlock"
          :key="node.position"
          :to="{
            name: 'browse',
            params: { ...route.params },
            query: {
              ...route.query,
              lvl: resource.level,
              pos: node.position,
            },
          }"
          @click="handleNodeClick"
        >
          <div class="cov-box" :class="node.covered && 'covered'" :title="node.label"></div>
        </router-link>
      </div>
    </div>

    <ButtonShelf top-gap>
      <n-button type="primary" @click="$emit('update:show', false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ButtonShelf>
  </n-modal>
</template>

<style scoped>
.cov-block {
  margin: var(--layout-gap) 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.cov-box {
  width: 24px;
  height: 24px;
  background-color: var(--main-bg-color);
  border-radius: var(--app-ui-border-radius);
  opacity: 0.8;
  transition: 0.2s;
}
.cov-box:hover {
  opacity: 1;
}

.cov-box.covered {
  background-color: var(--accent-color);
}
</style>
