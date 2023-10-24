<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import WysiwygEditor from '@/components/WysiwygEditor.vue';
import { ref } from 'vue';

const doc = ref('<p>FOO</p>');
</script>

<template>
  <h2>
    {{ $t('admin.system.segments.heading') }}
    <HelpButtonWidget help-key="adminSystemSegmentsView" />
  </h2>

  <div class="content-block">
    <WysiwygEditor v-model:document="doc" />
  </div>
</template>
