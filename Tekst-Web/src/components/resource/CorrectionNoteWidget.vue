<script setup lang="ts">
import { POST, type AnyResourceRead, type CorrectionCreate } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import PromptModal from '@/components/generic/PromptModal.vue';
import { useMessages } from '@/composables/messages';
import { correctionFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { CorrectionNoteIcon } from '@/icons';
import { useAuthStore, useBrowseStore, useResourcesStore } from '@/stores';
import { ref } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  locationId?: string;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const auth = useAuthStore();
const browse = useBrowseStore();
const resources = useResourcesStore();
const { message } = useMessages();

const promptModalRef = ref();

function handleClick() {
  promptModalRef.value.open();
  emit('done');
}

async function handleModalSubmit(note: string) {
  const locId = props.locationId || browse.locationPathHead?.id;
  if (!locId) {
    console.error('No location ID provided for correction note!');
    return;
  }

  const correction: CorrectionCreate = {
    resourceId: props.resource.id,
    locationId: locId,
    note,
  };
  const { data, error } = await POST('/corrections', {
    body: correction,
  });
  if (!error) {
    if (
      auth.user &&
      (auth.user.id === props.resource.ownerId || (auth.user.isSuperuser && props.resource.public))
    ) {
      const res = resources.all.find((r) => r.id === props.resource.id);
      if (!res) return;
      // increate resource correction counter
      resources.all = [
        ...resources.all.filter((r) => r.id !== props.resource.id),
        { ...res, corrections: (res.corrections ?? 0) + 1 },
      ];
      // add correction to resource corrections list
      resources.addCorrection(props.resource.id, data);
    }
    message.success($t('browse.contents.widgets.correctionNote.msgSuccess'));
  }
}
</script>

<template>
  <content-container-header-widget
    v-if="auth.loggedIn"
    v-bind="$attrs"
    :full="full"
    :title="$t('browse.contents.widgets.correctionNote.title')"
    :icon-component="CorrectionNoteIcon"
    @click="handleClick"
  />

  <prompt-modal
    ref="promptModalRef"
    type="textarea-osk"
    :title="$t('browse.contents.widgets.correctionNote.title')"
    :icon="CorrectionNoteIcon"
    :input-label="$t('browse.contents.widgets.correctionNote.lblNote')"
    :msg="$t('browse.contents.widgets.correctionNote.info')"
    :font="resource.config.general.font || undefined"
    :osk-mode-key="resource.config.general.osk || undefined"
    :rows="3"
    :validation-rules="correctionFormRules.note"
    @submit="(_, v) => handleModalSubmit(v)"
  />
</template>
