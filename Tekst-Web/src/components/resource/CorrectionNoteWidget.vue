<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { computed, ref } from 'vue';
import { POST, type AnyResourceRead, type CorrectionCreate } from '@/api';
import { useAuthStore, useBrowseStore, useResourcesStore } from '@/stores';
import { CorrectionNoteIcon } from '@/icons';
import PromptModal from '@/components/generic/PromptModal.vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { correctionFormRules } from '@/forms/formRules';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const auth = useAuthStore();
const browse = useBrowseStore();
const resources = useResourcesStore();
const { message } = useMessages();

const show = computed(() => !!auth.user);
const promptModalRef = ref();

function handleClick() {
  promptModalRef.value.open();
}

async function handleModalSubmit(note: string) {
  const correction: CorrectionCreate = {
    resourceId: props.resource.id,
    userId: auth.user?.id || '',
    position: browse.position,
    note,
  };
  const { data, error } = await POST('/corrections', {
    body: correction,
  });
  if (!error) {
    if (
      auth.user &&
      (auth.user.id == props.resource.ownerId || (auth.user.isSuperuser && props.resource.public))
    ) {
      const res = resources.ofText.find((r) => r.id == props.resource.id);
      if (!res) return;
      res.corrections ??= [];
      res.corrections.push(data);
    }
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
    :title="$t('browse.contents.widgets.correctionNote.heading')"
    :icon="CorrectionNoteIcon"
    :input-label="$t('browse.contents.widgets.correctionNote.lblNote')"
    :msg="$t('browse.contents.widgets.correctionNote.info')"
    :font="resource.config?.general?.font || undefined"
    :rows="3"
    :validation-rules="correctionFormRules.note"
    @submit="(_, v) => handleModalSubmit(v)"
  />
</template>
