<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import ResourceExportModal from '@/components/resource/ResourceExportModal.vue';
import { $t } from '@/i18n';
import { DownloadIcon } from '@/icons';
import { ref } from 'vue';

defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);
const show = ref(false);

function handleClick() {
  show.value = true;
  emit('done');
}
</script>

<template>
  <content-container-header-widget
    v-bind="$attrs"
    :full="full"
    :title="$t('common.export')"
    :icon-component="DownloadIcon"
    @click="handleClick"
  />
  <resource-export-modal v-model:show="show" :resource="resource" />
</template>
