<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import type { AnyResourceRead } from '@/api';

import { ClearIcon } from '@/icons';
import { pickTranslation } from '@/utils';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const state = useStateStore();
const browse = useBrowseStore();
const { message } = useMessages();

function handleClick() {
  browse.setResourcesActiveState([props.resource.id], false);
  message.info(
    $t('browse.contents.widgets.deactivateWidget.message', {
      resourceTitle: pickTranslation(props.resource.title, state.locale),
    })
  );
}
</script>

<template>
  <content-container-header-widget
    :title="$t('browse.contents.widgets.deactivateWidget.title')"
    :icon-component="ClearIcon"
    @click="handleClick"
  />
</template>
