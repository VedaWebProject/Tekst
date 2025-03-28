<script setup lang="ts">
import { DELETE, type AnyResourceRead, type CorrectionRead } from '@/api';
import LocationLabel from '@/components/LocationLabel.vue';
import { useMessages } from '@/composables/messages';
import { useUser } from '@/composables/user';
import { $t } from '@/i18n';
import { CorrectionNoteIcon, DeleteIcon, MessageIcon } from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore, useUserMessagesStore } from '@/stores';
import { getFullLocationLabel, pickTranslation, utcToLocalTime } from '@/utils';
import { NButton, NFlex, NIcon, NListItem, NThing, NTime } from 'naive-ui';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import UserDisplay from '../user/UserDisplay.vue';

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
const auth = useAuthStore();
const router = useRouter();
const resources = useResourcesStore();
const { message } = useMessages();
const { user } = useUser(props.correction.userId);
const userMessages = useUserMessagesStore();

const loading = ref(false);

function handleCorrectionClick(correction: CorrectionRead) {
  if (!props.clickable) return;
  router.push({
    name: 'resourceContents',
    params: {
      textSlug: state.text?.slug,
      resId: correction.resourceId,
      locId: correction.locationId,
    },
  });
}

async function deleteCorrection(correctionId: string) {
  loading.value = true;
  const { error } = await DELETE('/corrections/{id}', {
    params: { path: { id: correctionId } },
  });
  if (!error) {
    message.success($t('corrections.msgDeleted'));
    if (resources.corrections[props.resource.id]) {
      resources.corrections[props.resource.id] = resources.corrections[props.resource.id].filter(
        (c) => c.id !== correctionId
      );
      const res = resources.all.find((r) => r.id === props.resource.id);
      if (res) {
        res.corrections = (res.corrections ?? 1) - 1;
      }
    }
  }
  loading.value = false;
}

function handleMessageClick() {
  if (!user.value) return;
  const resTitle = pickTranslation(props.resource.title, state.locale);
  const locationLabel = getFullLocationLabel(
    props.correction.locationLabels.map((ll, i) => ({
      level: i,
      id: '',
      label: ll,
      position: 0,
      textId: state.text?.id || '',
    })),
    state.textLevelLabels,
    state.text
  );
  const prepMsg = `> ${resTitle}\n> ${locationLabel}\n> ${props.correction.note}\n\n`;
  userMessages.openConversation(user.value, prepMsg);
}
</script>

<template>
  <n-list-item
    :style="{ 'padding-left': indent ? 'var(--gap-lg)' : undefined }"
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
          <!-- open user message conversation -->
          <n-button
            v-if="user?.isActive && user.id !== auth.user?.id"
            secondary
            size="small"
            :focusable="false"
            :disabled="loading"
            :loading="loading"
            :title="
              $t('account.messages.btnSendMessageToUser', {
                username: user.name || `@${user.username}`,
              })
            "
            @click.stop.prevent="handleMessageClick"
          >
            <template #icon>
              <n-icon :component="MessageIcon" />
            </template>
          </n-button>
          <!-- delete correction note -->
          <n-button
            secondary
            size="small"
            type="error"
            :focusable="false"
            :disabled="loading"
            :loading="loading"
            :title="$t('common.delete')"
            @click.stop.prevent="deleteCorrection(correction.id)"
          >
            <template #icon>
              <n-icon :component="DeleteIcon" />
            </template>
          </n-button>
        </n-flex>
      </template>
      <template #description>
        <n-flex align="center">
          <user-display link :user="user || undefined" size="small" />
          <n-time
            class="translucent text-tiny"
            :time="utcToLocalTime(correction.date)"
            type="datetime"
          />
        </n-flex>
      </template>
      <template #default>
        <div
          class="pre-wrap"
          :style="{
            'font-family': resource.config.general.font || 'Tekst Content Font',
          }"
        >
          {{ correction.note }}
        </div>
      </template>
    </n-thing>
  </n-list-item>
</template>
