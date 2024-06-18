<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { computed, ref } from 'vue';
import { POST, type AnyResourceRead, type CorrectionCreate } from '@/api';
import { useAuthStore, useBrowseStore } from '@/stores';
import { CorrectionNoteIcon } from '@/icons';
import PromptModal from '@/components/generic/PromptModal.vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const auth = useAuthStore();
const browse = useBrowseStore();
const { message } = useMessages();

const show = computed(() => !!auth.user);
const promptModalRef = ref();

function handleClick() {
  promptModalRef.value.open();
}

async function handleModalSubmit(note: string) {
  const correction: CorrectionCreate = {
    resourceId: props.resource.id,
    position: browse.position,
    note,
  };
  const { error } = await POST('/corrections', {
    body: correction,
  });
  if (!error) {
    message.success($t('browse.contents.widgets.correctionNote.msgSuccess'));
  }
}
</script>

<template>
  <content-container-header-widget
    v-if="show"
    :title="$t('browse.contents.widgets.correctionNote.title')"
    :icon-component="CorrectionNoteIcon"
    @click="handleClick"
  />

  <prompt-modal
    ref="promptModalRef"
    multiline
    osk
    :font="resource.config?.general?.font || undefined"
    action-key="createBookmark"
    :title="$t('browse.contents.widgets.correctionNote.heading')"
    :input-label="$t('browse.contents.widgets.correctionNote.info')"
    :rows="3"
    :validation-rules="undefined"
    @submit="(_, v) => handleModalSubmit(v)"
  />
</template>
