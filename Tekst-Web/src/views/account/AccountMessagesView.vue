<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { DeleteIcon, MessageIcon, NoContentIcon } from '@/icons';
import { NButton, NIcon, NBadge, NSpace, NList, NListItem } from 'naive-ui';
import { useUserMessagesStore } from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import UserDisplay from '@/components/user/UserDisplay.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';

const { pfData } = usePlatformData();
const userMessages = useUserMessagesStore();

async function handleDeleteThread(e: UIEvent, id: string) {
  e.preventDefault();
  e.stopPropagation();
  await userMessages.deleteThread(id);
}
</script>

<template>
  <icon-heading level="1" :icon="MessageIcon">
    {{ $t('account.messages.heading') }}
    <help-button-widget help-key="accountMessagesView" />
  </icon-heading>

  <div v-if="userMessages.threads.length" class="text-small translucent">
    {{ $t('account.messages.msgUnreadCount', { count: userMessages.unreadCount }) }}
  </div>

  <div v-if="userMessages.threads.length" class="content-block">
    <h2>{{ $t('account.messages.headingThreads') }}</h2>
    <n-list
      hoverable
      clickable
      style="background-color: transparent"
      :style="{
        opacity: userMessages.loading ? 0.5 : 1,
        'pointer-events': userMessages.loading ? 'none' : 'auto',
      }"
    >
      <n-list-item
        v-for="thread in userMessages.threads"
        :key="thread.id"
        @click="
          () => {
            userMessages.openThread = thread;
            userMessages.showMessagingModal = true;
          }
        "
      >
        <n-space align="center">
          <n-badge :value="thread.unreadCount" :offset="[10, 0]">
            <user-display v-if="thread.contact" :user="thread.contact" :link="false" />
            <span v-else>{{ pfData?.settings.infoPlatformName || 'System' }}</span>
          </n-badge>
        </n-space>

        <template #suffix>
          <n-button
            secondary
            :title="$t('general.deleteAction')"
            @click="(e) => handleDeleteThread(e, thread.id)"
          >
            <template #icon>
              <n-icon :component="DeleteIcon" />
            </template>
          </n-button>
        </template>
      </n-list-item>
    </n-list>
  </div>

  <huge-labelled-icon
    v-else
    :icon="NoContentIcon"
    :message="$t('account.messages.msgNoMessages')"
  />
</template>
