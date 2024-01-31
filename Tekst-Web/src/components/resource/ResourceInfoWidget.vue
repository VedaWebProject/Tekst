<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { NEllipsis, NDivider, NButton, NProgress } from 'naive-ui';
import MetadataDisplay from '@/components/resource/MetadataDisplay.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { type AnyResourceRead, type ResourceCoverage } from '@/api';
import UserDisplay from '@/components/user/UserDisplay.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import ResourcePublicationStatus from '@/components/resource/ResourcePublicationStatus.vue';
import CoverageDetailsWidget from './CoverageDetailsWidget.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import ResourceIsVersionInfo from '@/components/resource/ResourceIsVersionInfo.vue';

import {
  InfoIcon,
  CommentIcon,
  FormatQuoteIcon,
  CoverageIcon,
  MetadataIcon,
  ResourceIcon,
} from '@/icons';

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
  <content-container-header-widget
    :title="$t('browse.contents.widgets.infoWidget.title')"
    :icon-component="InfoIcon"
    @click="showInfoModal = true"
  />

  <generic-modal v-model:show="showInfoModal" :title="resource.title" :icon="ResourceIcon">
    <p v-if="resource.description?.length">
      <translation-display :value="resource.description" />
    </p>

    <template v-if="auth.loggedIn">
      <p class="resource-status-box">
        <user-display :user="resource.owner ?? undefined" size="tiny" />
        <resource-publication-status :resource="resource" size="tiny" />
        <resource-is-version-info :resource="resource" size="tiny" />
      </p>
      <n-divider />
    </template>

    <template v-if="resource.meta && Object.keys(resource.meta).length">
      <icon-heading level="3" :icon="MetadataIcon">
        {{ $t('models.meta.modelLabel') }}
      </icon-heading>
      <metadata-display :data="resource.meta" />
      <n-divider />
    </template>

    <template v-if="resource.citation">
      <icon-heading level="3" :icon="FormatQuoteIcon">
        {{ $t('browse.contents.widgets.infoWidget.citeAs') }}
      </icon-heading>
      <div>
        {{ resource.citation }}
      </div>
      <n-divider />
    </template>

    <template v-if="coverage">
      <icon-heading level="3" :icon="CoverageIcon">
        {{ $t('browse.contents.widgets.infoWidget.coverage') }}
      </icon-heading>

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
            $t('browse.contents.widgets.infoWidget.coverageStatement', {
              present: coverage.covered,
              total: coverage.total,
              level: state.textLevelLabels[resource.level],
            })
          }}
        </span>
        <span style="flex: 2"></span>
        <template v-if="auth.loggedIn">
          <n-button
            quaternary
            type="primary"
            size="small"
            :focusable="false"
            @click="showCoverageDetailsModal = true"
          >
            {{ $t('general.details') }}
          </n-button>
        </template>
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
      <n-divider />
    </template>

    <template v-if="resource.comment?.length">
      <icon-heading level="3" :icon="CommentIcon">
        {{ $t('models.resource.comment') }}
      </icon-heading>
      <div class="resource-comment">
        <n-ellipsis :tooltip="false" :line-clamp="2" expand-trigger="click">
          <translation-display :value="resource.comment" />
        </n-ellipsis>
      </div>
    </template>

    <button-shelf top-gap>
      <n-button type="primary" @click="() => (showInfoModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>

  <coverage-details-widget
    v-if="auth.loggedIn"
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
