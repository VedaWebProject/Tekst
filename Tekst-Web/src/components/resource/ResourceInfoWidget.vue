<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import CollapsibleContent from '@/components/CollapsibleContent.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import MetadataDisplay from '@/components/resource/MetadataDisplay.vue';
import ResourceCoverageWidget from '@/components/resource/ResourceCoverageWidget.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import {
  CoverageIcon,
  DescIcon,
  FormatQuoteIcon,
  InfoIcon,
  MetadataIcon,
  ResourceIcon,
} from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NDivider, NFlex } from 'naive-ui';
import { computed, ref } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const auth = useAuthStore();
const state = useStateStore();

const title = computed(() => pickTranslation(props.resource.title, state.locale));
const descriptionHtml = computed(() => pickTranslation(props.resource.description, state.locale));
const showInfoModal = ref(false);
</script>

<template>
  <content-container-header-widget
    :full="full"
    :title="$t('common.information')"
    :icon-component="InfoIcon"
    @click="
      () => {
        showInfoModal = true;
        emit('done');
      }
    "
  />

  <generic-modal v-model:show="showInfoModal" :title="title" :icon="ResourceIcon" width="wide">
    <n-flex v-if="auth.loggedIn" justify="space-between" class="mb-lg">
      <user-display :user="resource.owner || undefined" size="small" :system="!resource.owner" />
      <resource-info-tags :resource="resource" reverse />
    </n-flex>

    <!-- SUBTITLE -->
    <p v-if="resource.subtitle.length" :style="{ fontFamily: resource.contentFont }">
      <translation-display :value="resource.subtitle" />
      <n-divider />
    </p>

    <!-- METADATA -->
    <template v-if="resource.meta && Object.keys(resource.meta).length">
      <icon-heading level="3" :icon="MetadataIcon">
        {{ $t('models.meta.modelLabel') }}
      </icon-heading>
      <metadata-display :data="resource.meta" :content-font="resource.contentFont" />
      <n-divider />
    </template>

    <!-- CITATION -->
    <template v-if="resource.citation">
      <icon-heading level="3" :icon="FormatQuoteIcon">
        {{ $t('browse.contents.widgets.infoWidget.citeAs') }}
      </icon-heading>
      <div :style="{ fontFamily: resource.contentFont }">
        {{ resource.citation }}
      </div>
      <n-divider />
    </template>

    <!-- DESCRIPTION -->
    <template v-if="!!descriptionHtml">
      <icon-heading level="3" :icon="DescIcon">
        {{ $t('common.description') }}
      </icon-heading>
      <collapsible-content>
        <hydrated-html :html="descriptionHtml" :style="{ fontFamily: resource.contentFont }" />
      </collapsible-content>
      <n-divider />
    </template>

    <!-- COVERAGE -->
    <icon-heading level="3" :icon="CoverageIcon">
      {{ $t('browse.contents.widgets.infoWidget.coverage') }}
    </icon-heading>
    <resource-coverage-widget :resource="resource" @navigate="showInfoModal = false" />

    <button-shelf top-gap>
      <n-button type="primary" @click="() => (showInfoModal = false)">
        {{ $t('common.close') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
