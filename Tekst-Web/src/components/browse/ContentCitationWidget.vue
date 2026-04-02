<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import { commonDialogOptions } from '@/common';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { $t } from '@/i18n';
import { QuoteIcon } from '@/icons';
import { renderIcon } from '@/utils';
import { useDialog } from 'naive-ui';
import { h } from 'vue';
import ContentCitationWidgetContent from './ContentCitationWidgetContent.vue';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const dialog = useDialog();

function handleClick() {
  dialog.create({
    ...commonDialogOptions,
    icon: renderIcon(QuoteIcon, undefined, 'large'),
    title: $t('models.resource.citation'),
    contentClass: 'my-lg',
    content: () => h(ContentCitationWidgetContent, { resource: props.resource }),
    style: 'width: 600px',
  });

  emit('done');
}
</script>

<template>
  <content-container-header-widget
    v-bind="$attrs"
    :full="full"
    :title="$t('models.resource.citation')"
    :icon-component="QuoteIcon"
    @click="handleClick"
  />
</template>
