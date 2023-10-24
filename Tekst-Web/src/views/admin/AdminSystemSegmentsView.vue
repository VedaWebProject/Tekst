<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
</script>

<template>
  <h2>
    {{ $t('admin.system.segments.heading') }}
    <HelpButtonWidget help-key="adminSystemSegmentsView" />
  </h2>

  <div class="content-block">SEGMENTS!!!</div>
</template>
