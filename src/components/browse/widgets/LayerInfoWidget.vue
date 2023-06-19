<script setup lang="ts">
import { computed, ref } from 'vue';
import { NButton, NModal, NProgress } from 'naive-ui';
import MetadataDisplay from '@/components/browse/MetadataDisplay.vue';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';
import InfoOutlined from '@vicons/material/InfoOutlined';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useProfile, useLayerCoverage } from '@/fetchers';
import { useStateStore } from '@/stores';

const props = defineProps<{
  data: Record<string, any>;
}>();

const state = useStateStore();

const showInfoModal = ref(false);
const { user: owner, error: ownerError } = useProfile(props.data.ownerId, showInfoModal);
const { coverage, error: coverageError } = useLayerCoverage(props.data.id, showInfoModal);
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
    :title="$t('models.meta.modelLabel')"
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
    <h2>{{ data.title }}</h2>

    <p>
      {{ $t(`layerTypes.${data.layerType}`) }}
      {{ $t('models.meta.onLevel', { level: state.textLevelLabels[data.level] }) }}.
    </p>

    <p v-if="owner && !ownerError">
      {{ $t('models.meta.providedBy') }}:
      <RouterLink :to="{ name: 'user', params: { username: owner.username } }">{{
        ownerDisplayName
      }}</RouterLink>
    </p>

    <template v-if="Object.keys(data.meta as object).length">
      <h3>{{ $t('models.meta.modelLabel') }}</h3>
      <MetadataDisplay :data="data.meta" />
    </template>

    <template v-if="data.comment">
      <h3>{{ $t('models.meta.comment') }}</h3>
      <div class="layer-comment">
        {{ data.comment }}
      </div>
    </template>

    <template v-if="coverage && !coverageError">
      <h3>{{ $t('browse.infoWidget.coverage') }}</h3>
      <p>
        {{
          $t('browse.infoWidget.coverageStatement', {
            present: presentNodes,
            total: coverage.length,
            level: state.textLevelLabels[data.level],
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
        rail-color="var(--accent-color-fade5)"
      />
    </template>

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
  font-size: var(--app-ui-font-size-medium);
}
</style>
