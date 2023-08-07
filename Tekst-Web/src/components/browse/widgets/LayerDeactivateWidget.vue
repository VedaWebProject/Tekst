<script setup lang="ts">
import ClearRound from '@vicons/material/ClearRound';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useBrowseStore } from '@/stores';
import { useMessages } from '@/messages';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  layer: Record<string, any>;
}>();

const browse = useBrowseStore();
const { message } = useMessages();
const { t } = useI18n({ useScope: 'global' });

function handleClick() {
  const layer = browse.layers.find((l) => l.id == props.layer.id);
  layer && (layer.active = false);
  message.info(
    t('browse.units.widgets.deactivateWidget.message', { layerTitle: props.layer.title })
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
