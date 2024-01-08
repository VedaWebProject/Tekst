<script setup lang="ts">
import { computed, ref } from 'vue';
import { NEllipsis, NDivider, NButton, NModal, NProgress, NSpin } from 'naive-ui';
import MetadataDisplay from '@/components/browse/MetadataDisplay.vue';
import ButtonFooter from '@/components/ButtonFooter.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useResourceCoverage } from '@/fetchers';
import { useAuthStore, useStateStore } from '@/stores';
import type { AnyResourceRead } from '@/api';
import UserDisplay from '@/components/UserDisplay.vue';
import TranslationDisplay from '@/components/TranslationDisplay.vue';
import ResourcePublicationStatus from '@/components/ResourcePublicationStatus.vue';

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

const showInfoModal = ref(false);
const { coverage, error: coverageError } = useResourceCoverage(props.resource.id, showInfoModal); // eslint-disable-line
const presentNodes = computed(
  () => coverage.value && coverage.value.filter((n) => n.covered).length
);
const coveragePercent = computed(
  () =>
    (coverage.value &&
      presentNodes.value &&
      Math.round((presentNodes.value / coverage.value.length) * 100)) ||
    0
);
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.infoWidget.title')"
    :icon-component="InfoOutlined"
    @click="showInfoModal = true"
  />

  <n-modal
    v-model:show="showInfoModal"
    preset="card"
    class="tekst-modal"
    :title="resource.title"
    :bordered="false"
    :auto-focus="false"
    :closable="true"
    header-style="padding-bottom: .25rem"
    to="#app-container"
    embedded
  >
    <template #header>
      <h2 style="margin: 0">{{ resource.title }}</h2>
    </template>

    <p v-if="resource.description?.length">
      <TranslationDisplay :value="resource.description" />
    </p>

    <p>
      <UserDisplay v-if="auth.loggedIn" :user="resource.owner ?? undefined" size="tiny" />
      <ResourcePublicationStatus v-if="auth.loggedIn" :resource="resource" size="tiny" />
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
      <p>
        {{
          $t('browse.units.widgets.infoWidget.coverageStatement', {
            present: presentNodes,
            total: coverage.length,
            level: state.textLevelLabels[resource.level],
          })
        }}
      </p>
      <n-progress
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
      <n-divider />
      {{ $t('errors.unexpected') }}
    </template>
    <n-spin v-else style="width: 100%" />

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

    <ButtonFooter>
      <n-button type="primary" @click="() => (showInfoModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ButtonFooter>
  </n-modal>
</template>

<style scoped>
.resource-comment {
  white-space: pre-wrap;
  font-weight: var(--app-ui-font-weight-light);
}
</style>
