<script setup lang="ts">
import { type AnyLayerRead, AnyLayerUpdate } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useMessages } from '@/messages';

import LayersFilled from '@vicons/material/LayersFilled';

const props = defineProps<{
  layer?: AnyLayerRead;
}>();

const auth = useAuthStore();
const { message } = useMessages();

const getInitialModel = () => {
  if (props.layer) {
    return {
      ...props.layer,
    };
  } else {
    return {};
  }
};
</script>

<template>
  <IconHeading level="1" :icon="LayersFilled">
    {{ $t('dataLayers.heading') }} {{ layers ? `(${layers?.length})` : '' }}
    <HelpButtonWidget help-key="dataLayersView" />
  </IconHeading>
</template>
