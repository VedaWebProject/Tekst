<script setup lang="ts">
import { computed, ref } from 'vue';
import { NButton, NModal, NProgress, NSpin, NIcon } from 'naive-ui';
import MetadataDisplay from '@/components/browse/MetadataDisplay.vue';
import ButtonFooter from '@/components/ButtonFooter.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useLayerCoverage } from '@/fetchers';
import { useAuthStore, useStateStore } from '@/stores';
import type { AnyLayerRead } from '@/api';
import UserDisplay from '@/components/UserDisplay.vue';
import TranslationDisplay from '@/components/TranslationDisplay.vue';
import LayerPublicationStatus from '@/components/LayerPublicationStatus.vue';

import InfoOutlined from '@vicons/material/InfoOutlined';
import ChatBubbleOutlineOutlined from '@vicons/material/ChatBubbleOutlineOutlined';
import FormatQuoteFilled from '@vicons/material/FormatQuoteFilled';
import PercentOutlined from '@vicons/material/PercentOutlined';
import PersonFilled from '@vicons/material/PersonFilled';
import LabelOutlined from '@vicons/material/LabelOutlined';

const props = defineProps<{
  layer: AnyLayerRead;
}>();

const auth = useAuthStore();
const state = useStateStore();

const showInfoModal = ref(false);
const { coverage, error: coverageError } = useLayerCoverage(props.layer.id, showInfoModal); // eslint-disable-line
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
    :icon-component="InfoOutlined"
    @click="showInfoModal = true"
  />

  <n-modal
    v-model:show="showInfoModal"
    preset="card"
    class="tekst-modal"
    size="large"
    :title="layer.title"
    :bordered="false"
    :auto-focus="false"
    :closable="true"
    header-style="padding-bottom: .25rem"
    to="#app-container"
    embedded
  >
    <template #header>
      <h2 style="margin: 0">{{ layer.title }}</h2>
    </template>

    <p v-if="layer.description?.length">
      <TranslationDisplay :value="layer.description" />
    </p>

    <p
      v-if="layer.owner"
      style="display: flex; align-items: center; font-size: var(--app-ui-font-size-small)"
    >
      <n-icon :component="PersonFilled" style="margin-right: 4px" />
      <RouterLink :to="{ name: 'user', params: { username: layer.owner.username } }">
        <UserDisplay :user="layer.owner" />
      </RouterLink>
    </p>

    <p v-if="auth.loggedIn">
      <LayerPublicationStatus :layer="layer" />
    </p>

    <template v-if="layer.meta && Object.keys(layer.meta).length">
      <IconHeading level="3" :icon="LabelOutlined">
        {{ $t('models.meta.modelLabel') }}
      </IconHeading>
      <MetadataDisplay :data="layer.meta" />
    </template>

    <template v-if="layer.citation">
      <IconHeading level="3" :icon="FormatQuoteFilled">
        {{ $t('browse.units.widgets.infoWidget.citeAs') }}
      </IconHeading>
      <div>
        {{ layer.citation }}
      </div>
    </template>

    <IconHeading level="3" :icon="PercentOutlined">
      {{ $t('browse.units.widgets.infoWidget.coverage') }}
    </IconHeading>
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

    <template v-if="layer.comment?.length">
      <IconHeading level="3" :icon="ChatBubbleOutlineOutlined">
        {{ $t('models.layer.comment') }}
      </IconHeading>
      <div class="layer-comment">
        <TranslationDisplay :value="layer.comment" />
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
.layer-comment {
  white-space: pre-wrap;
  font-weight: var(--app-ui-font-weight-light);
}
</style>
