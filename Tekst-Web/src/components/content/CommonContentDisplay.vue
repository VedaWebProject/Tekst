<script setup lang="ts">
import type { AnyContentRead } from '@/api';
import { CommentIcon } from '@/icons';
import { NAlert, NFlex, NIcon } from 'naive-ui';

defineProps<{
  authorsComment?: AnyContentRead['authorsComment'];
  editorsComments?: AnyContentRead['editorsComments'];
  showComments?: boolean;
  font?: string;
}>();
</script>

<template>
  <div class="common-content-display">
    <slot></slot>

    <n-alert
      v-if="showComments && !!authorsComment"
      :title="$t('resources.types.common.contentFields.authorsComment')"
      class="mt-md"
    >
      <template #icon>
        <n-icon :component="CommentIcon" :size="16" />
      </template>
      <div class="pre-wrap text-small" :style="{ fontFamily: font }">
        {{ authorsComment }}
      </div>
    </n-alert>

    <n-alert
      v-if="showComments && !!editorsComments"
      :title="$t('resources.types.common.contentFields.editorsComments')"
      class="mt-md"
    >
      <template #icon>
        <n-icon :component="CommentIcon" :size="16" />
      </template>
      <n-flex vertical size="small">
        <div
          v-for="(cmt, i) in editorsComments"
          :key="i"
          class="text-small divided"
          :style="{
            fontFamily: font,
            paddingBottom: i < editorsComments.length - 1 ? 'var(--gap-sm)' : undefined,
          }"
        >
          <div class="pre-wrap">{{ cmt.comment }}</div>
          <div class="i font-ui">– {{ cmt.by }}</div>
        </div>
      </n-flex>
    </n-alert>
  </div>
</template>

<style scoped>
.common-content-display:not(:last-child) {
  padding-bottom: var(--gap-md);
  margin-bottom: var(--gap-md);
  border-bottom: 1px solid var(--main-bg-color);
}

.common-content-display:last-child {
  margin-bottom: 4px;
}
</style>
