<script setup lang="ts">
import type { AnyContentRead } from '@/api';
import { CommentIcon } from '@/icons';
import { NFlex, NIcon } from 'naive-ui';

defineProps<{
  comments?: AnyContentRead['comments'];
  showComments?: boolean;
  font?: string;
}>();
</script>

<template>
  <div class="common-content-display">
    <slot></slot>

    <div v-if="showComments && !!comments" class="comments-container text-small mt-lg">
      <n-flex class="mb-sm translucent" align="center" :wrap="false">
        <n-icon :component="CommentIcon" />
        <span>{{ $t('resources.types.common.comments') }}</span>
      </n-flex>
      <n-flex vertical size="small">
        <div v-for="(cmt, i) in comments" :key="i" class="comment" :style="{ fontFamily: font }">
          <div class="pre-wrap">{{ cmt.comment }}</div>
          <div v-if="cmt.by" class="i font-ui">– {{ cmt.by }}</div>
        </div>
      </n-flex>
    </div>
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

.common-content-display .comments-container {
  padding: var(--gap-sm) var(--gap-lg);
  border-radius: var(--border-radius);
  border: 1px dashed var(--text-color-translucent);
}

.comment {
  border-bottom: 1px solid var(--main-bg-color);
  margin-bottom: var(--gap-sm);
  padding-bottom: var(--gap-sm);
}

.comment:last-child {
  border-bottom: none;
  margin-bottom: unset;
  padding-bottom: unset;
}
</style>
