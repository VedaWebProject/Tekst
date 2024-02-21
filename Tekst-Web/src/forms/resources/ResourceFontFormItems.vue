<script setup lang="ts">
import { usePlatformData } from '@/composables/platformData';
import { NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

defineProps<{
  value?: string;
}>();

defineEmits(['update:value']);

const { pfData } = usePlatformData();

const options = computed(
  () =>
    pfData.value?.settings.customFonts?.map((f) => ({
      label: f,
      value: f,
    })) || []
);
</script>

<template>
  <n-form-item
    v-if="options.length"
    :label="$t('resources.settings.config.general.font')"
    :show-feedback="false"
    style="margin-top: var(--layout-gap)"
  >
    <n-select
      clearable
      :value="value"
      :options="options"
      @update:value="(v) => $emit('update:value', v)"
    />
  </n-form-item>
</template>
