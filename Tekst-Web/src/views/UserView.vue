<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import UserAvatar from '@/components/user/UserAvatar.vue';
import UserThingHeader from '@/components/user/UserThingHeader.vue';
import { useUser } from '@/composables/user';
import { MessageIcon, UserIcon } from '@/icons';
import { useAuthStore, useStateStore, useUserMessagesStore } from '@/stores';
import { NButton, NIcon, NSpin, NThing } from 'naive-ui';
import { computed, watchEffect } from 'vue';
import { useRoute } from 'vue-router';

const props = defineProps<{
  username?: string;
}>();

const route = useRoute();
const auth = useAuthStore();
const state = useStateStore();
const userMessages = useUserMessagesStore();

const usernameOrId = computed(() => {
  if (route.name && route.name === 'user' && props.username) {
    return props.username;
  } else if (route.name === 'accountProfile') {
    return auth.user?.username || '';
  }
  return '';
});
const { user, loading, error } = useUser(usernameOrId);

watchEffect(() => {
  state.setPageTitle(route, { username: usernameOrId.value });
});
</script>

<template>
  <icon-heading level="1" :icon="UserIcon">
    {{ $t('account.profileHeading') }}
  </icon-heading>

  <n-spin v-if="loading" :description="$t('common.loading')" class="centered-spinner" />

  <div v-else-if="error" class="content-block">
    <h1>Oops... {{ $t('errors.error') }}!</h1>
    <i class="translucent">{{ $t('account.profileNotFound', { usernameOrId }) }}</i>
  </div>

  <div v-else-if="user && !error" class="content-block">
    <n-thing :content-indented="!state.smallScreen">
      <template #avatar>
        <user-avatar :avatar-url="user.avatarUrl || undefined" :size="64" />
      </template>

      <template #header>
        <user-thing-header :user="user" />
      </template>

      <template v-if="auth.user && user.id !== auth.user.id && user.isActive" #header-extra>
        <n-button
          type="primary"
          circle
          size="large"
          :title="
            $t('account.messages.btnSendMessageToUser', {
              username: user.name || `@${user.username}`,
            })
          "
          @click="() => userMessages.openConversation(user?.id || '?')"
        >
          <template #icon>
            <n-icon :component="MessageIcon" />
          </template>
        </n-button>
      </template>

      <template #default>
        <p v-if="user.bio" class="pre-wrap">
          {{ user.bio }}
        </p>
        <p v-else class="translucent text-small i">
          {{ $t('account.profileNoBio') }}
        </p>
      </template>
    </n-thing>
  </div>
</template>
