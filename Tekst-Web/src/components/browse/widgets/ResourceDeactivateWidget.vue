<script setup lang="ts">
import ClearRound from '@vicons/material/ClearRound';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useBrowseStore } from '@/stores';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import type { AnyResourceRead } from '@/api';

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
    :icon-component="ClearRound"
    @click="handleClick"
  />
</template>
