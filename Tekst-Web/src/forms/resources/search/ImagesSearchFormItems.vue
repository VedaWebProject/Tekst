<script setup lang="ts">
import type { ImagesResourceRead, ImagesSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: ImagesResourceRead;
  queryIndex: number;
}>();

const model = defineModel<ImagesSearchQuery>({ required: true });
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('general.caption')"
    :path="`queries[${queryIndex}].rts.caption`"
    :rule="searchFormRules.images.caption"
  >
    <n-input-osk
      v-model="model.caption"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
      :placeholder="$t('general.caption')"
    />
  </n-form-item>
</template>
