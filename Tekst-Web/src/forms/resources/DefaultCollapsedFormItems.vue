<script setup lang="ts">
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { NFormItem } from 'naive-ui';

defineProps<{
  value?: boolean;
}>();

defineEmits(['update:value']);
</script>

<template>
  <n-form-item :show-label="false" :show-feedback="false">
    <LabelledSwitch
      :value="value"
      :label="$t('resources.settings.config.general.defaultCollapsed')"
      @update:value="(v) => $emit('update:value', v)"
    />
  </n-form-item>
</template>
