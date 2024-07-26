<script setup lang="ts">
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { NFormItem } from 'naive-ui';

const model = defineModel<boolean>();
</script>

<template>
  <n-form-item :show-label="false">
    <labelled-switch
      v-model="model"
      :label="$t('resources.settings.config.general.defaultCollapsed')"
    />
  </n-form-item>
</template>
