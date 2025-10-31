<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { CommentIcon } from '@/icons';
import { computed } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const showComments = defineModel<boolean>('showComments');
const emit = defineEmits(['done']);

const authorsComments = computed(
  () => props.resource.contents?.map((c) => c.authorsComment).filter(Boolean) || []
);
const editorsComments = computed(
  () => props.resource.contents?.map((c) => c.editorsComments).filter(Boolean) || []
);
const hasComments = computed(
  () => !!authorsComments.value.length || !!editorsComments.value.length
);
</script>

<template>
  <content-container-header-widget
    v-if="hasComments"
    :full="full"
    :title="$t('common.comment', 2)"
    :icon-component="CommentIcon"
    :toggled="showComments"
    :highlight="hasComments && !showComments"
    @click="
      () => {
        showComments = !showComments;
        emit('done');
      }
    "
  />
</template>
