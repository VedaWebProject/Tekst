<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import FormSection from '@/components/FormSection.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { $t } from '@/i18n';
import { NFormItem } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<boolean>({
  required: true,
});
</script>

<template>
  <form-section :title="$t('resources.settings.config.locationMetadata.embedAsTagsHeading')">
    <n-form-item :show-label="false">
      <labeled-switch
        v-model="model"
        :label="$t('resources.settings.config.locationMetadata.embedAsTags')"
      />
    </n-form-item>
  </form-section>
</template>
