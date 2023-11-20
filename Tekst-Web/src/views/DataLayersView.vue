<script setup lang="ts">
import IconHeading from '@/components/typography/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import LayersFilled from '@vicons/material/LayersFilled';
</script>

<template>
  <IconHeading level="1" :icon="LayersFilled">
    {{ $t('dataLayers.heading') }}
    <HelpButtonWidget help-key="dataLayersView" />
  </IconHeading>
</template>

<style scoped></style>
