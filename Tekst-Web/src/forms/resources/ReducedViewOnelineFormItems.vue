<script setup lang="ts">
import { NCheckbox, NFormItem } from 'naive-ui';

defineProps<{
  value?: boolean;
}>();

defineEmits(['update:value']);
</script>

<template>
  <n-form-item :show-label="false" :show-feedback="false">
    <n-checkbox :checked="value" @update:checked="(v) => $emit('update:value', v)">
      {{ $t('resources.settings.config.general.reducedViewOneline') }}
    </n-checkbox>
  </n-form-item>
</template>
