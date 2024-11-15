<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import MetadataDisplay from '@/components/resource/MetadataDisplay.vue';
import ResourceCoverageWidget from '@/components/resource/ResourceCoverageWidget.vue';
import ResourceIsVersionInfo from '@/components/resource/ResourceIsVersionInfo.vue';
import ResourcePublicationStatus from '@/components/resource/ResourcePublicationStatus.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { CommentIcon, CoverageIcon, FormatQuoteIcon, InfoIcon, MetadataIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NDivider, NEllipsis, NFlex } from 'naive-ui';
import { computed, ref } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const auth = useAuthStore();
const state = useStateStore();

const resourceTitle = computed(() => pickTranslation(props.resource.title, state.locale));
const showInfoModal = ref(false);
</script>

<template>
  <content-container-header-widget
    :full="full"
    :title="$t('browse.contents.widgets.infoWidget.title')"
    :icon-component="InfoIcon"
    @click="
      () => {
        showInfoModal = true;
        emit('done');
      }
    "
  />

  <generic-modal v-model:show="showInfoModal" :title="resourceTitle" :icon="InfoIcon" width="wide">
    <!-- USER -->
    <user-display
      v-if="auth.loggedIn && !!resource.owner"
      :user="resource.owner"
      size="tiny"
      class="mb-lg"
    />

    <!-- PUBLICATION, VERSION -->
    <div v-if="auth.loggedIn" class="gray-box">
      <n-flex vertical>
        <resource-publication-status :resource="resource" size="tiny" />
        <resource-is-version-info v-if="resource.originalId" :resource="resource" size="tiny" />
      </n-flex>
    </div>

    <!-- DESCRIPTION -->
    <p v-if="resource.description.length">
      <translation-display :value="resource.description" />
    </p>

    <!-- METADATA -->
    <template v-if="resource.meta && Object.keys(resource.meta).length">
      <icon-heading level="3" :icon="MetadataIcon">
        {{ $t('models.meta.modelLabel') }}
      </icon-heading>
      <metadata-display :data="resource.meta" />
      <n-divider />
    </template>

    <!-- CITATION -->
    <template v-if="resource.citation">
      <icon-heading level="3" :icon="FormatQuoteIcon">
        {{ $t('browse.contents.widgets.infoWidget.citeAs') }}
      </icon-heading>
      <div>
        {{ resource.citation }}
      </div>
      <n-divider />
    </template>

    <!-- COMMENT -->
    <template v-if="resource.comment.length">
      <icon-heading level="3" :icon="CommentIcon">
        {{ $t('general.comment') }}
      </icon-heading>
      <div class="resource-comment">
        <n-ellipsis :tooltip="false" :line-clamp="2" expand-trigger="click">
          <translation-display :value="resource.comment" />
        </n-ellipsis>
      </div>
      <n-divider />
    </template>

    <!-- COVERAGE -->
    <icon-heading level="3" :icon="CoverageIcon">
      {{ $t('browse.contents.widgets.infoWidget.coverage') }}
    </icon-heading>
    <resource-coverage-widget :resource="resource" @navigate="showInfoModal = false" />

    <button-shelf top-gap>
      <n-button type="primary" @click="() => (showInfoModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped>
.resource-comment {
  white-space: pre-wrap;
}
</style>
