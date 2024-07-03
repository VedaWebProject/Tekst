<script setup lang="ts">
import { DELETE, type CorrectionRead, type AnyResourceRead } from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { CorrectionNoteIcon, DeleteIcon, UserIcon } from '@/icons';
import { useResourcesStore, useStateStore } from '@/stores';
import { utcToLocalTime } from '@/utils';
import { NListItem, NThing, NIcon, NButton, NFlex, NTime, NAlert } from 'naive-ui';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import LocationLabel from '@/components/LocationLabel.vue';

const props = withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    correction: CorrectionRead;
    clickable?: boolean;
    indent?: boolean;
  }>(),
  {
    clickable: true,
  }
);

const state = useStateStore();
const router = useRouter();
const resources = useResourcesStore();
const { message } = useMessages();

const loading = ref(false);

function handleCorrectionClick(correction: CorrectionRead) {
  if (!props.clickable) return;
  router.push({
    name: 'resourceContents',
    params: { text: state.text?.slug, id: correction.resourceId, pos: correction.position },
  });
}

async function deleteCorrection(e: UIEvent, correctionId: string) {
  e.stopPropagation();
  e.preventDefault();
  loading.value = true;
  const { error } = await DELETE('/corrections/{id}', {
    params: { path: { id: correctionId } },
  });
  if (!error) {
    message.success($t('corrections.msgDeleted'));
    if (props.resource.corrections) {
      resources.corrections[props.resource.id] = resources.corrections[props.resource.id].filter(
        (c) => c.id !== correctionId
      );
      const res = resources.all.find((r) => r.id === props.resource.id);
      if (res) {
        res.corrections = res.corrections != null ? res.corrections - 1 : 0;
      }
    }
  }
  loading.value = false;
}

function gotoUserProfile(e: UIEvent, userId: string) {
  e.stopPropagation();
  e.preventDefault();
  router.push({ name: 'user', params: { username: userId } });
}
</script>

<template>
  <n-list-item
    :style="{ 'padding-left': indent ? 'var(--layout-gap)' : undefined }"
    @click="handleCorrectionClick(correction)"
  >
    <n-thing
      :content-indented="!state.smallScreen"
      description-style="font-size: var(--font-size-tiny)"
    >
      <template #avatar>
        <n-icon :component="CorrectionNoteIcon" size="large" />
      </template>
      <template #header>
        <location-label :location-labels="correction.locationLabels" />
      </template>
      <template #header-extra>
        <n-flex align="center" :wrap="false" style="height: 100%">
          <n-button
            secondary
            size="small"
            :focusable="false"
            :disabled="loading"
            :loading="loading"
            :title="$t('models.user.modelLabel')"
            @click="(e) => gotoUserProfile(e, correction.userId)"
          >
            <template #icon>
              <n-icon :component="UserIcon" />
            </template>
          </n-button>
          <n-button
            secondary
            size="small"
            type="error"
            :focusable="false"
            :disabled="loading"
            :loading="loading"
            :title="$t('general.deleteAction')"
            @click="(e) => deleteCorrection(e, correction.id)"
          >
            <template #icon>
              <n-icon :component="DeleteIcon" />
            </template>
          </n-button>
        </n-flex>
      </template>
      <template #description>
        <n-time
          class="translucent text-tiny"
          :time="utcToLocalTime(correction.date)"
          type="datetime"
        />
      </template>
      <template #default>
        <n-alert
          :show-icon="false"
          :style="{
            'white-space': 'pre-wrap',
            'font-family': resource.config?.general?.font || 'Tekst Content Font',
          }"
        >
          {{ correction.note }}
        </n-alert>
      </template>
    </n-thing>
  </n-list-item>
</template>
