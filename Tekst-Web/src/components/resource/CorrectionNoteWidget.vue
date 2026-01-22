<script setup lang="ts">
import { POST, type AnyResourceRead, type CorrectionCreate } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useMessages } from '@/composables/messages';
import { usePrompt } from '@/composables/prompt';
import { $t } from '@/i18n';
import { CorrectionNoteIcon } from '@/icons';
import { useAuthStore, useBrowseStore, useResourcesStore } from '@/stores';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    full?: boolean;
    showInfo?: boolean;
  }>(),
  {
    showInfo: true,
  }
);

const emit = defineEmits(['done']);

const auth = useAuthStore();
const browse = useBrowseStore();
const resources = useResourcesStore();
const { message } = useMessages();
const prompt = usePrompt();

const enabled = computed(() => !!auth.user && props.resource.contents?.length === 1);
const widgetTitle = computed(() =>
  enabled.value
    ? $t('browse.contents.widgets.correctionNote.title')
    : $t('browse.contents.widgets.correctionNote.disabledTip')
);

async function handleClick() {
  emit('done'); // closes mobile widget drawer as soon as widget is clicked

  const note = await prompt({
    type: 'multiLineInputOSK',
    title: $t('browse.contents.widgets.correctionNote.title'),
    icon: CorrectionNoteIcon,
    label: $t('browse.contents.widgets.correctionNote.lblNote'),
    rows: 3,
    maxLength: 2000,
    msg: props.showInfo ? $t('browse.contents.widgets.correctionNote.info') : undefined,
    font: props.resource.config.general.font || undefined,
    oskKey: props.resource.config.general.osk || undefined,
  });

  if (!note) return;

  const locId = browse.locationPath[props.resource.level]?.id;
  if (!locId) {
    console.error('Cannot determine current content location.');
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
      (props.resource.ownerIds.includes(auth.user.id) ||
        (auth.user.isSuperuser && props.resource.public))
    ) {
      const res = resources.all.find((r) => r.id === props.resource.id);
      if (!res) return;
      // increase resource correction counter
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
    v-if="!!auth.user"
    :disabled="!enabled"
    v-bind="$attrs"
    :full="full"
    :title="widgetTitle"
    :icon-component="CorrectionNoteIcon"
    @click="handleClick"
  />
</template>
