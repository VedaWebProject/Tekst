<script setup lang="ts">
import type { AudioResourceRead, AudioSearchQuery } from '@/api';
import OskInput from '@/components/OskInput.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: AudioResourceRead;
  queryIndex: number;
}>();

const model = defineModel<AudioSearchQuery>({ required: true });
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('common.caption')"
    :path="`queries[${queryIndex}].rts.caption`"
    :rule="searchFormRules.audio.caption"
  >
    <osk-input
      v-model="model.caption"
      :placeholder="$t('common.caption')"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.general.osk || undefined"
    />
  </n-form-item>
</template>
