<script setup lang="ts">
import { computed, ref } from 'vue';
import { NButton, NModal, NProgress, NSpin } from 'naive-ui';
import MetadataDisplay from '@/components/browse/MetadataDisplay.vue';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';
import InfoOutlined from '@vicons/material/InfoOutlined';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useProfile, useLayerCoverage } from '@/fetchers';
import { useStateStore } from '@/stores';

const props = defineProps<{
  layer: Record<string, any>;
}>();

const state = useStateStore();

const showInfoModal = ref(false);
const { user: owner, error: ownerError } = useProfile(props.layer.ownerId, showInfoModal); // eslint-disable-line
const { coverage, error: coverageError } = useLayerCoverage(props.layer.id, showInfoModal); // eslint-disable-line
const ownerDisplayName = computed(
  () =>
    (owner.value &&
      (owner.value.firstName && owner.value.lastName
        ? `${owner.value.firstName} ${owner.value.lastName}`
        : owner.value.username)) ||
    ''
);
const presentNodes = computed(
  () => coverage.value && coverage.value.filter((n) => n.covered).length
);
const coveragePercent = computed(
  () =>
    coverage.value &&
    presentNodes.value &&
    Math.round((presentNodes.value / coverage.value.length) * 100)
);
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.infoWidget.title')"
    :iconComponent="InfoOutlined"
    @click="showInfoModal = true"
  />

  <n-modal
    v-model:show="showInfoModal"
    preset="card"
    class="tekst-modal"
    size="large"
    :bordered="false"
    :auto-focus="false"
    :closable="false"
    to="#app-container"
    embedded
  >
    <h2>{{ layer.title }}</h2>

    <p>
      {{ $t(`layerTypes.${layer.layerType}`) }}
      {{ $t('models.meta.onLevel', { level: state.textLevelLabels[layer.level] }) }}.
    </p>

    <p v-if="owner && !ownerError">
      {{ $t('models.meta.providedBy') }}:
      <RouterLink :to="{ name: 'user', params: { username: owner.username } }">{{
        ownerDisplayName
      }}</RouterLink>
    </p>

    <template v-if="Object.keys(layer.meta as object).length">
      <h3>{{ $t('models.meta.modelLabel') }}</h3>
      <MetadataDisplay :data="layer.meta" />
    </template>

    <template v-if="layer.comment">
      <h3>{{ $t('models.meta.comment') }}</h3>
      <div class="layer-comment">
        {{ layer.comment }}
      </div>
    </template>

    <h3>{{ $t('browse.units.widgets.infoWidget.coverage') }}</h3>
    <template v-if="coverage">
      <p>
        {{
          $t('browse.units.widgets.infoWidget.coverageStatement', {
            present: presentNodes,
            total: coverage.length,
            level: state.textLevelLabels[layer.level],
          })
        }}
      </p>
      <n-progress
        v-if="coveragePercent"
        type="line"
        :percentage="coveragePercent"
        :height="18"
        :border-radius="4"
        indicator-placement="inside"
        color="var(--accent-color)"
        rail-color="var(--accent-color-fade4)"
      />
    </template>
    <template v-else-if="coverageError">
      {{ $t('errors.unexpected') }}
    </template>
    <n-spin v-else style="width: 100%" />

    <ModalButtonFooter>
      <n-button type="primary" @click="() => (showInfoModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ModalButtonFooter>
  </n-modal>
</template>

<style scoped>
.layer-comment {
  white-space: pre-wrap;
  font-weight: var(--app-ui-font-weight-light);
}
</style>
