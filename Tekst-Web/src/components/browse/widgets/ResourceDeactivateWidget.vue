<script setup lang="ts">
import ClearRound from '@vicons/material/ClearRound';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
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
    $t('browse.units.widgets.deactivateWidget.message', { resourceTitle: props.resource.title })
  );
}
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.deactivateWidget.title')"
    :icon-component="ClearRound"
    @click="handleClick"
  />
</template>
