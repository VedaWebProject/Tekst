<script setup lang="ts">
import { $t } from '@/i18n';
import { CompressIcon, ExpandIcon } from '@/icons';
import { useElementSize } from '@vueuse/core';
import { NButton, NIcon } from 'naive-ui';
import { computed, ref } from 'vue';

const props = withDefaults(
  defineProps<{
    collapsable?: boolean;
    heightTreshPx?: number;
    collapseText?: string;
    expandText?: string;
    scrollable?: boolean;
    showBtnText?: boolean;
  }>(),
  {
    collapsable: true,
    heightTreshPx: 150,
    collapseText: $t('general.collapseAction'),
    expandText: $t('general.expandAction'),
    scrollable: true,
    showBtnText: true,
  }
);

const contentRef = ref<HTMLElement>();
const { height } = useElementSize(contentRef);
const collapsed = defineModel<boolean>({ required: false, default: true });
const isCollapsable = computed(() => props.collapsable && height.value > props.heightTreshPx);
const isCollapsed = computed(() => isCollapsable.value && collapsed.value);
</script>

<template>
  <div>
    <div
      :class="{ collapsed: isCollapsed }"
      :style="{
        maxHeight: isCollapsed ? `${heightTreshPx}px` : undefined,
        overflow: scrollable || !isCollapsed ? 'scroll' : 'hidden',
      }"
    >
      <div ref="contentRef">
        <slot></slot>
      </div>
    </div>
    <n-button
      v-if="isCollapsable"
      text
      block
      class="mt-sm"
      :focusable="false"
      :size="showBtnText ? undefined : 'large'"
      @click.stop.prevent="collapsed = !collapsed"
    >
      <template #icon>
        <n-icon :component="isCollapsed ? ExpandIcon : CompressIcon" />
      </template>
      <template v-if="showBtnText">
        {{ isCollapsed ? expandText : collapseText }}
      </template>
    </n-button>
  </div>
</template>

<style scoped>
.collapsed {
  box-shadow: rgba(0, 0, 0, 0.175) 0px -40px 12px -40px inset;
  border-radius: var(--border-radius);
}
</style>
