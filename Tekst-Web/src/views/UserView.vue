<script setup lang="ts">
import { useProfile } from '@/composables/fetchers';
import { computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { NButton, NSpin, NThing, NIcon } from 'naive-ui';
import { useAuthStore, useUserMessagesStore, useStateStore } from '@/stores';
import IconHeading from '@/components/generic/IconHeading.vue';
import UserAvatar from '@/components/user/UserAvatar.vue';
import UserThingHeader from '@/components/user/UserThingHeader.vue';
import { MessageIcon, UserIcon } from '@/icons';
import type { UserMessageThread } from '@/api';

const route = useRoute();
const auth = useAuthStore();
const state = useStateStore();
const userMessages = useUserMessagesStore();

const username = computed(() => {
  if (route.name) {
    if (route.name === 'user' && route.params.username) {
      return String(route.params.username);
    } else if (route.name === 'accountProfile') {
      return auth.user?.username || '';
    }
  }
  return '';
});
const { user, error } = useProfile(username);

function handleSendUserMessage() {
  if (!user.value || !auth.loggedIn) return;
  const thread: UserMessageThread = userMessages.threads.find(
    (t) => user.value && t.id === user.value.id
  ) || {
    id: user.value.id,
    contact: user.value,
    unread: 0,
  };
  userMessages.openThread = thread;
  userMessages.showMessagingModal = true;
}

watch(
  () => username.value,
  (newUsername) => {
    state.setPageTitle(route, { username: newUsername });
  },
  { immediate: true }
);
</script>

<template>
  <icon-heading level="1" :icon="UserIcon">
    {{ $t('account.profileHeading') }}
  </icon-heading>

  <div v-if="user && !error" class="content-block">
    <n-thing content-indented>
      <template #avatar>
        <user-avatar :avatar-url="user.avatarUrl || undefined" :size="64" />
      </template>

      <template #header>
        <user-thing-header :user="user" />
      </template>

      <template v-if="auth.user" #header-extra>
        <n-button
          type="primary"
          circle
          size="large"
          :disabled="user.id === auth.user.id || !user.isActive"
          :title="$t('account.messages.btnSendMessageToUser', { username: user.username })"
          @click="handleSendUserMessage"
        >
          <template #icon>
            <n-icon :component="MessageIcon" />
          </template>
        </n-button>
      </template>

      <template #default>
        <p v-if="user.bio" style="white-space: pre-wrap">
          {{ user.bio }}
        </p>
        <p v-else class="translucent text-small i">
          {{ $t('account.profileNoBio') }}
        </p>
      </template>
    </n-thing>
  </div>

  <n-spin v-else-if="!error" :description="$t('general.loading')" class="centered-spinner" />

  <div v-else class="content-block">
    <h1>Oops... {{ $t('errors.error') }}!</h1>
    {{ $t('account.profileNotFound', { username }) }}
  </div>
</template>
