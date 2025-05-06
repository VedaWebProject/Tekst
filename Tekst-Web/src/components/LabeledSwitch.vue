<script setup lang="ts">
import { $t } from '@/i18n';
import { NFlex, NIcon, NSwitch } from 'naive-ui';
import { computed, type Component } from 'vue';

const props = withDefaults(
  defineProps<{
    label?: string;
    onLabel?: string;
    offLabel?: string;
    showLabel?: boolean;
    iconOn?: Component;
    iconOff?: Component;
    round?: boolean;
    size?: 'small' | 'medium' | 'large';
    disabled?: boolean;
    loading?: boolean;
    focusable?: boolean;
    onValue?: string | number | boolean;
    offValue?: string | number | boolean;
  }>(),
  {
    showLabel: true,
    onValue: true,
    offValue: false,
    size: 'medium',
  }
);

const model = defineModel<string | number | boolean>();
const effectiveLabel = computed(() =>
  !props.showLabel
    ? undefined
    : props.label
      ? props.label
      : model.value == (props.onValue !== undefined ? props.onValue : true)
        ? props.onLabel || $t('common.on')
        : props.offLabel || $t('common.off')
);

const labelLineHeight = computed(
  () => ({ small: '20px', medium: '22px', large: '28px' })[props.size]
);
</script>

<template>
  <n-flex :wrap="false" style="padding: 6px 0">
    <n-switch
      v-model:value="model"
      :round="!!round"
      :size="size"
      :disabled="disabled"
      :loading="loading"
      :focusable="focusable"
      :checked-value="onValue !== undefined ? onValue : true"
      :unchecked-value="offValue !== undefined ? offValue : false"
    >
      <template #checked-icon>
        <n-icon :component="iconOn" />
      </template>
      <template #unchecked-icon>
        <n-icon :component="iconOff" />
      </template>
    </n-switch>
    <span
      v-if="!!effectiveLabel"
      :class="{
        translucent: disabled,
        'text-small': size === 'small',
        'text-medium': size === 'medium',
        'text-large': size === 'large',
      }"
      :style="{ lineHeight: labelLineHeight }"
    >
      {{ effectiveLabel }}
    </span>
  </n-flex>
</template>
