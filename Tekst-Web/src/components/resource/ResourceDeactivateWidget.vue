<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useBrowseStore } from '@/stores';
import { $t } from '@/i18n';
import type { AnyResourceRead } from '@/api';

import { ClearIcon } from '@/icons';

const props = defineProps<{
  resource: AnyResourceRead;
  small?: boolean;
}>();

const browse = useBrowseStore();

function handleClick() {
  browse.setResourcesActiveState([props.resource.id], false);
}
</script>

<template>
  <content-container-header-widget
    :title="$t('browse.contents.widgets.deactivateWidget.title')"
    :icon-component="ClearIcon"
    :small="small"
    @click="handleClick"
  />
</template>
