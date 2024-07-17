<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useBrowseStore } from '@/stores';
import { $t } from '@/i18n';
import type { AnyResourceRead } from '@/api';

import { ClearIcon } from '@/icons';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const browse = useBrowseStore();

function handleClick() {
  browse.setResourcesActiveState([props.resource.id], false);
  emit('done');
}
</script>

<template>
  <content-container-header-widget
    :full="full"
    :title="$t('browse.contents.widgets.deactivateWidget.title')"
    :icon-component="ClearIcon"
    @click="handleClick"
  />
</template>
