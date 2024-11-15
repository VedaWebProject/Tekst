<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import ContentCommentWidget from '@/components/resource/ContentCommentWidget.vue';
import ContentEditWidget from '@/components/resource/ContentEditWidget.vue';
import CorrectionNoteWidget from '@/components/resource/CorrectionNoteWidget.vue';
import LocationContentSiblingsWidget from '@/components/resource/LocationContentSiblingsWidget.vue';
import contentWidgets from '@/components/resource/mappings';
import ResourceDeactivateWidget from '@/components/resource/ResourceDeactivateWidget.vue';
import ResourceExportWidget from '@/components/resource/ResourceExportWidget.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourceSettingsWidget from '@/components/resource/ResourceSettingsWidget.vue';
import { MoreIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NIcon } from 'naive-ui';
import { computed, ref } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    opacity?: number;
    smallScreen?: boolean;
  }>(),
  {
    opacity: 1,
  }
);

const state = useStateStore();

const showWidgetsModal = ref(false);
const closeModal = () => (showWidgetsModal.value = false);
const resourceTitle = computed(() => pickTranslation(props.resource?.title, state.locale));

function handleSmallScreenWidgetsTriggered() {
  showWidgetsModal.value = !showWidgetsModal.value;
}
</script>

<template>
  <div v-if="!smallScreen" class="content-header-widgets" :style="{ opacity }">
    <!-- resource-type-specific widgets -->
    <template v-if="resource.contents?.length">
      <template
        v-for="(configSection, configSectionKey) in resource.config"
        :key="configSectionKey"
      >
        <component
          :is="contentWidgets[configSectionKey]"
          v-if="configSectionKey in contentWidgets"
          :widget-config="configSection"
          :resource="resource"
        />
      </template>
    </template>
    <!-- generic content widgets -->
    <location-content-siblings-widget :resource="resource" />
    <content-comment-widget :resource="resource" />
    <correction-note-widget :resource="resource" />
    <resource-export-widget :resource="resource" />
    <content-edit-widget :resource="resource" />
    <resource-settings-widget :resource="resource" />
    <resource-info-widget :resource="resource" />
    <resource-deactivate-widget :resource="resource" />
  </div>

  <n-button
    v-else
    quaternary
    circle
    :focusable="false"
    :style="{ opacity }"
    @click.stop.prevent="handleSmallScreenWidgetsTriggered"
  >
    <template #icon>
      <n-icon :component="MoreIcon" />
    </template>
  </n-button>

  <generic-modal
    v-if="smallScreen"
    v-model:show="showWidgetsModal"
    display-directive="show"
    width="narrow"
    :title="resourceTitle"
    :icon="MoreIcon"
    heading-level="3"
  >
    <div class="content-header-widgets small-screen-widgets">
      <!-- resource-type-specific widgets -->
      <template v-if="resource.contents?.length">
        <template
          v-for="(configSection, configSectionKey) in resource.config"
          :key="configSectionKey"
        >
          <component
            :is="contentWidgets[configSectionKey]"
            v-if="configSectionKey in contentWidgets"
            :widget-config="configSection"
            :resource="resource"
            full
            @done="closeModal"
          />
        </template>
      </template>
      <!-- generic content widgets -->
      <location-content-siblings-widget :resource="resource" full @done="closeModal" />
      <correction-note-widget :resource="resource" full @done="closeModal" />
      <resource-export-widget :resource="resource" full @done="closeModal" />
      <content-comment-widget :resource="resource" full @done="closeModal" />
      <content-edit-widget :resource="resource" full @done="closeModal" />
      <resource-settings-widget :resource="resource" full @done="closeModal" />
      <resource-info-widget :resource="resource" full @done="closeModal" />
      <resource-deactivate-widget :resource="resource" full @done="closeModal" />
    </div>
  </generic-modal>
</template>

<style scoped>
.content-header-widgets {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  gap: 8px;
  transition: opacity 0.2s ease;
}

.small-screen-widgets {
  flex-direction: column-reverse;
  align-items: flex-start;
  gap: 16px;
}
</style>
