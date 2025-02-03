<script setup lang="ts">
import type { AudioResourceRead, AudioSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
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
    :label="$t('general.caption')"
    :path="`queries[${queryIndex}].rts.caption`"
    :rule="searchFormRules.audio.caption"
  >
    <n-input-osk
      v-model="model.caption"
      :placeholder="$t('general.caption')"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
    />
  </n-form-item>
</template>
