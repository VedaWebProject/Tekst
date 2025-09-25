<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import ContentCommentWidget from '@/components/resource/ContentCommentWidget.vue';
import ContentEditWidget from '@/components/resource/ContentEditWidget.vue';
import CorrectionNoteWidget from '@/components/resource/CorrectionNoteWidget.vue';
import DeepLLinksWidget from '@/components/resource/DeepLLinksWidget.vue';
import JumpToContentWidget from '@/components/resource/JumpToContentWidget.vue';
import LocationContentContextWidget from '@/components/resource/LocationContentContextWidget.vue';
import ResourceDeactivateWidget from '@/components/resource/ResourceDeactivateWidget.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourceSettingsWidget from '@/components/resource/ResourceSettingsWidget.vue';
import { MoreIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NFlex, NIcon } from 'naive-ui';
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

const showComments = defineModel<boolean>('showComments');
const state = useStateStore();

const showWidgetsModal = ref(false);
const closeModal = () => (showWidgetsModal.value = false);
const resourceTitle = computed(() => pickTranslation(props.resource?.title, state.locale));

function handleSmallScreenWidgetsTriggered() {
  showWidgetsModal.value = !showWidgetsModal.value;
}
</script>

<template>
  <n-flex
    v-if="!smallScreen"
    justify="center"
    align="center"
    :wrap="false"
    class="content-header-widgets"
    :style="{ opacity }"
    size="small"
  >
    <!-- resource-type-specific widgets -->
    <deep-l-links-widget :resource="resource" />
    <!-- generic widgets -->
    <location-content-context-widget :resource="resource" :show-comments="showComments" />
    <content-comment-widget v-model:show-comments="showComments" :resource="resource" />
    <correction-note-widget :resource="resource" />
    <content-edit-widget :resource="resource" />
    <resource-settings-widget :resource="resource" />
    <jump-to-content-widget :resource="resource" direction="before" />
    <jump-to-content-widget :resource="resource" direction="after" />
    <resource-info-widget :resource="resource" />
    <resource-deactivate-widget :resource="resource" />
  </n-flex>

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
    <n-flex
      justify="center"
      align="flex-start"
      size="small"
      :wrap="false"
      class="content-header-widgets"
      style="flex-direction: column-reverse"
    >
      <!-- resource-type-specific widgets -->
      <deep-l-links-widget :resource="resource" full @done="closeModal" />
      <!-- generic content widgets -->
      <location-content-context-widget :resource="resource" full @done="closeModal" />
      <correction-note-widget :resource="resource" full @done="closeModal" />
      <content-comment-widget :resource="resource" full @done="closeModal" />
      <content-edit-widget :resource="resource" full @done="closeModal" />
      <resource-settings-widget :resource="resource" full @done="closeModal" />
      <jump-to-content-widget :resource="resource" direction="before" full @done="closeModal" />
      <jump-to-content-widget :resource="resource" direction="after" full @done="closeModal" />
      <resource-info-widget :resource="resource" full @done="closeModal" />
      <resource-deactivate-widget :resource="resource" full @done="closeModal" />
    </n-flex>
  </generic-modal>
</template>

<style scoped>
.content-header-widgets {
  transition: opacity 0.2s ease;
}
</style>
