<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useBrowseStore } from '@/stores';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import type { AnyResourceRead } from '@/api';

import { ClearIcon } from '@/icons';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const browse = useBrowseStore();
const { message } = useMessages();

function handleClick() {
  browse.setResourceActiveState(props.resource.id, false);
  message.info(
    $t('browse.contents.widgets.deactivateWidget.message', { resourceTitle: props.resource.title })
  );
}
</script>

<template>
  <ContentContainerHeaderWidget
    :title="$t('browse.contents.widgets.deactivateWidget.title')"
    :icon-component="ClearIcon"
    @click="handleClick"
  />
</template>
