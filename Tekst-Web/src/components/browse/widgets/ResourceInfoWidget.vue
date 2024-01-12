<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { NEllipsis, NDivider, NButton, NProgress } from 'naive-ui';
import MetadataDisplay from '@/components/browse/MetadataDisplay.vue';
import ButtonShelf from '@/components/ButtonShelf.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { type AnyResourceRead, type ResourceCoverage } from '@/api';
import UserDisplay from '@/components/UserDisplay.vue';
import TranslationDisplay from '@/components/TranslationDisplay.vue';
import ResourcePublicationStatus from '@/components/ResourcePublicationStatus.vue';
import CoverageDetailsWidget from './CoverageDetailsWidget.vue';
import GenericModal from '@/components/GenericModal.vue';
import ResourceIsVersionInfo from '@/components/ResourceIsVersionInfo.vue';

import InfoOutlined from '@vicons/material/InfoOutlined';
import ChatBubbleOutlineOutlined from '@vicons/material/ChatBubbleOutlineOutlined';
import FormatQuoteFilled from '@vicons/material/FormatQuoteFilled';
import PercentOutlined from '@vicons/material/PercentOutlined';
import LabelOutlined from '@vicons/material/LabelOutlined';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const auth = useAuthStore();
const state = useStateStore();
const resources = useResourcesStore();

const showCoverageDetailsModal = ref(false);
const showInfoModal = ref(false);
const coverage = ref<ResourceCoverage>();
const coveragePercent = computed(
  () => Math.round((coverage.value ? coverage.value.covered / coverage.value.total : 0) * 1000) / 10
);

watch(showInfoModal, async (after) => {
  if (after) {
    coverage.value = await resources.getCoverage(props.resource.id);
  }
});
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.infoWidget.title')"
    :icon-component="InfoOutlined"
    @click="showInfoModal = true"
  />

  <GenericModal v-model:show="showInfoModal" :title="resource.title" :icon="InfoOutlined">
    <p v-if="resource.description?.length">
      <TranslationDisplay :value="resource.description" />
    </p>

    <p v-if="auth.loggedIn" class="resource-status-box">
      <UserDisplay :user="resource.owner ?? undefined" size="tiny" />
      <ResourcePublicationStatus :resource="resource" size="tiny" />
      <ResourceIsVersionInfo :resource="resource" size="tiny" />
    </p>

    <template v-if="resource.meta && Object.keys(resource.meta).length">
      <n-divider />
      <IconHeading level="3" :icon="LabelOutlined">
        {{ $t('models.meta.modelLabel') }}
      </IconHeading>
      <MetadataDisplay :data="resource.meta" />
    </template>

    <template v-if="resource.citation">
      <n-divider />
      <IconHeading level="3" :icon="FormatQuoteFilled">
        {{ $t('browse.units.widgets.infoWidget.citeAs') }}
      </IconHeading>
      <div>
        {{ resource.citation }}
      </div>
    </template>

    <template v-if="coverage">
      <n-divider />
      <IconHeading level="3" :icon="PercentOutlined">
        {{ $t('browse.units.widgets.infoWidget.coverage') }}
      </IconHeading>

      <div
        style="
          display: flex;
          justify-content: flex-end;
          align-items: center;
          margin-bottom: 0.5rem;
          gap: 12px;
        "
      >
        <span>
          {{
            $t('browse.units.widgets.infoWidget.coverageStatement', {
              present: coverage.covered,
              total: coverage.total,
              level: state.textLevelLabels[resource.level],
            })
          }}
        </span>
        <span style="flex: 2"></span>
        <n-button
          quaternary
          type="primary"
          size="small"
          :focusable="false"
          @click="showCoverageDetailsModal = true"
        >
          {{ $t('general.details') }}
        </n-button>
      </div>
      <n-progress
        type="line"
        :percentage="coveragePercent"
        :height="16"
        :border-radius="3"
        indicator-placement="inside"
        color="var(--accent-color)"
        rail-color="var(--accent-color-fade4)"
      />
    </template>

    <template v-if="resource.comment?.length">
      <n-divider />
      <IconHeading level="3" :icon="ChatBubbleOutlineOutlined">
        {{ $t('models.resource.comment') }}
      </IconHeading>
      <div class="resource-comment">
        <n-ellipsis :tooltip="false" :line-clamp="2" expand-trigger="click">
          <TranslationDisplay :value="resource.comment" />
        </n-ellipsis>
      </div>
    </template>

    <ButtonShelf top-gap>
      <n-button type="primary" @click="() => (showInfoModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>

  <CoverageDetailsWidget
    v-model:show="showCoverageDetailsModal"
    :resource="resource"
    :coverage-basic="coverage"
    @navigated="showInfoModal = false"
  />
</template>

<style scoped>
.resource-status-box {
  padding: 0.5rem;
  background-color: var(--main-bg-color);
  border-radius: var(--app-ui-border-radius);
}
.resource-comment {
  white-space: pre-wrap;
  font-weight: var(--app-ui-font-weight-light);
}
</style>
