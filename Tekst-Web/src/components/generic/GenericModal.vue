<script setup lang="ts">
import { NModal } from 'naive-ui';
import type { ModalProps } from 'naive-ui';
import { computed, type Component, type CSSProperties } from 'vue';
import IconHeading from '@/components/generic/IconHeading.vue';

const props = withDefaults(
  defineProps<{
    show?: boolean;
    size?: 'small' | 'medium' | 'large' | 'huge';
    width?: 'narrow' | 'medium' | 'wide' | 'full';
    to?: string;
    title?: string;
    icon?: Component;
    headingLevel?: '1' | '2' | '3' | '4' | '5' | '6';
    closable?: boolean;
    autoFocus?: boolean;
    nuiModalProps?: ModalProps;
  }>(),
  {
    show: false,
    size: undefined,
    width: 'medium',
    to: '#app-container',
    title: undefined,
    icon: undefined,
    headingLevel: '2',
    closable: true,
    nuiModalProps: undefined,
  }
);

const emit = defineEmits([
  'update:show',
  'maskClick',
  'afterEnter',
  'afterLeave',
  'esc',
  'vue:mounted',
  'close',
]);

const modalStyle = computed<CSSProperties>(() => ({
  maxWidth: '95%',
  width: {
    narrow: '480px',
    medium: '600px',
    wide: '900px',
    full: 'var(--max-app-width)',
  }[props.width],
}));

function handleMaskClick(e: MouseEvent) {
  emit('maskClick', e);
  emit('update:show', false);
}
</script>

<template>
  <n-modal
    embedded
    display-directive="if"
    preset="card"
    header-style="padding-bottom: var(--layout-gap);"
    v-bind="nuiModalProps"
    :closable="closable"
    :bordered="false"
    :size="size"
    :show="show"
    :auto-focus="autoFocus"
    :style="modalStyle"
    :to="to"
    @update:show="emit('update:show', $event)"
    @mask-click="(e) => handleMaskClick(e)"
    @esc="(e) => emit('esc', e)"
    @vue:mounted="emit('vue:mounted')"
    @after-enter="emit('afterEnter')"
    @after-leave="emit('afterLeave')"
    @close="emit('close')"
  >
    <template #header>
      <slot name="header">
        <IconHeading v-if="title" :level="headingLevel" :icon="icon" style="margin: 0">
          {{ title }}
        </IconHeading>
      </slot>
    </template>
    <slot></slot>
  </n-modal>
</template>
