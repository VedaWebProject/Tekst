<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { AudioResourceRead, AudioSearchQuery } from '@/api';
import { searchFormRules } from '@/forms/formRules';

defineProps<{
  resource: AudioResourceRead;
  queryIndex: number;
}>();

const model = defineModel<AudioSearchQuery>({ required: true });

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('general.caption')"
    :path="`queries[${queryIndex}].rts.caption`"
    :rule="searchFormRules.audio.caption"
  >
    <n-input-osk
      :model-value="model.caption"
      :placeholder="$t('general.caption')"
      @update:model-value="(v) => handleUpdate('caption', v)"
    />
  </n-form-item>
</template>
