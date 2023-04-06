<script setup lang="ts">
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import TranslateRound from '@vicons/material/TranslateRound';
import type { DeepLLinksConfig } from '@/openapi';

const props = defineProps<{
  widgetConfig?: DeepLLinksConfig;
  unitData?: Record<string, any>;
}>();

function handleClick() {
  console.log('TRANSLATE!!!', props.unitData?.text, props.widgetConfig);
}
</script>

<template v-if="props.widgetConfig.enabled && props.unitData?.text && props.widgetConfig">
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.tipDeepLTranslate')"
    :iconComponent="TranslateRound"
    @click="handleClick"
  />
</template>
