<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { $t } from '@/i18n';
import { NFormItem } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<boolean>({
  required: true,
});
</script>

<template>
  <form-section-heading
    :label="$t('resources.settings.config.locationMetadata.embedAsTagsHeading')"
  />

  <!-- enabled -->
  <n-form-item :show-label="false">
    <labeled-switch
      v-model="model"
      :label="$t('resources.settings.config.locationMetadata.embedAsTags')"
    />
  </n-form-item>
</template>
