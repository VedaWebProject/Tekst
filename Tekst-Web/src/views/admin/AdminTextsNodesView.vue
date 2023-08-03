<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { useStateStore } from '@/stores';

const state = useStateStore();
const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <h1>{{ t('admin.heading') }}: {{ state.text?.title }} - {{ t('admin.texts.nodes.heading') }}</h1>

  <div class="content-block">FOO</div>
</template>
