<script setup lang="ts">
import type { AnyContentRead } from '@/api';
import { CommentIcon } from '@/icons';
import { NFlex, NIcon } from 'naive-ui';

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

    <div
      v-if="showComments && !!authorsComment"
      :title="$t('resources.types.common.contentFields.authorsComment')"
      class="comment-container text-small mt-lg"
    >
      <n-flex class="mb-sm translucent" align="center" :wrap="false">
        <n-icon :component="CommentIcon" />
        <span>{{ $t('resources.types.common.contentFields.authorsComment') }}</span>
      </n-flex>
      <div class="pre-wrap text-small" :style="{ fontFamily: font, paddingLeft: '30px' }">
        {{ authorsComment }}
      </div>
    </div>

    <div v-if="showComments && !!editorsComments" class="comment-container text-small mt-lg">
      <n-flex class="mb-sm translucent" align="center" :wrap="false">
        <n-icon :component="CommentIcon" />
        <span>{{ $t('resources.types.common.contentFields.editorsComments') }}</span>
      </n-flex>
      <n-flex vertical size="small" style="padding-left: 30px">
        <div
          v-for="(cmt, i) in editorsComments"
          :key="i"
          class="divided"
          :style="{
            fontFamily: font,
            paddingBottom: i < editorsComments.length - 1 ? 'var(--gap-md)' : undefined,
          }"
        >
          <div class="pre-wrap">{{ cmt.comment }}</div>
          <div class="i font-ui">– {{ cmt.by }}</div>
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

.common-content-display .comment-container {
  padding: var(--gap-sm) var(--gap-md);
  border-radius: var(--border-radius);
  border: 1px dashed var(--text-color-translucent);
}
</style>
