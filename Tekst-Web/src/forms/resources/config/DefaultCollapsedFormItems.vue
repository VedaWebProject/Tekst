<script setup lang="ts">
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { NFormItem } from 'naive-ui';

const model = defineModel<boolean>();
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.general.defaultCollapsed')" />
  <n-form-item :show-label="false">
    <labeled-switch v-model="model" />
  </n-form-item>
</template>
