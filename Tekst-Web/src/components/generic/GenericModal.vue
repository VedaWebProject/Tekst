<script setup lang="ts">
import { NModal } from 'naive-ui';
import { computed, type Component, type CSSProperties } from 'vue';
import IconHeading from '@/components/generic/IconHeading.vue';

const props = withDefaults(
  defineProps<{
    width?: 'narrow' | 'medium' | 'wide' | 'full';
    to?: string;
    title?: string;
    icon?: Component;
    headingLevel?: '1' | '2' | '3' | '4' | '5' | '6';
  }>(),
  {
    width: 'medium',
    to: '#app-container',
    title: undefined,
    icon: undefined,
    headingLevel: '2',
  }
);

const show = defineModel<boolean>('show');

const modalStyle = computed<CSSProperties>(() => ({
  maxWidth: '95%',
  marginTop: 'var(--layout-gap)',
  marginBottom: 'var(--layout-gap)',
  width: {
    narrow: '480px',
    medium: '600px',
    wide: '900px',
    full: 'var(--max-app-width)',
  }[props.width],
}));
</script>

<template>
  <n-modal
    v-model:show="show"
    v-bind="$attrs"
    :to="to"
    embedded
    display-directive="if"
    preset="card"
    header-style="padding-bottom: var(--layout-gap);"
    :bordered="false"
    :style="modalStyle"
  >
    <template #header>
      <slot name="header">
        <icon-heading v-if="title" :level="headingLevel" :icon="icon" style="margin: 0">
          {{ title }}
        </icon-heading>
      </slot>
    </template>
    <template #header-extra>
      <slot name="header-extra"></slot>
    </template>
    <slot></slot>
    <template #cover>
      <slot name="cover"></slot>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
    <template #action>
      <slot name="action"></slot>
    </template>
  </n-modal>
</template>
