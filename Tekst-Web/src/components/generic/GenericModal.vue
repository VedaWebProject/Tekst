<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { useStateStore } from '@/stores';
import { NModal } from 'naive-ui';
import { type Component } from 'vue';

const props = withDefaults(
  defineProps<{
    width?: 'narrow' | 'medium' | 'wide' | 'full';
    to?: string;
    title?: string;
    icon?: Component;
    headingLevel?: '1' | '2' | '3' | '4' | '5' | '6';
    nodeClass?: string;
  }>(),
  {
    width: 'medium',
    to: undefined,
    title: undefined,
    icon: undefined,
    headingLevel: '2',
  }
);

const show = defineModel<boolean>('show', { default: false });
const state = useStateStore();

const modalWidths = {
  narrow: '480px',
  medium: '600px',
  wide: '900px',
  full: 'var(--max-app-width)',
};
</script>

<template>
  <n-modal
    v-model:show="show"
    :to="to"
    display-directive="if"
    preset="card"
    :size="state.smallScreen ? 'small' : undefined"
    :bordered="false"
    :style="{ width: modalWidths[props.width], maxWidth: '95%' }"
    class="mx-auto my-md"
    :class="nodeClass"
  >
    <template #header>
      <slot name="header">
        <icon-heading v-if="title" :level="headingLevel" :icon="icon" class="m-0">
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
