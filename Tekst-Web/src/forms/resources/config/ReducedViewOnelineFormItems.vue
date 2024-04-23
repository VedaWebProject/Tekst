<script setup lang="ts">
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { NFormItem } from 'naive-ui';

const model = defineModel<boolean>();
</script>

<template>
  <n-form-item :show-label="false" :show-feedback="false">
    <labelled-switch
      v-model="model"
      :label="$t('resources.settings.config.general.reducedViewOneline')"
    />
  </n-form-item>
</template>
