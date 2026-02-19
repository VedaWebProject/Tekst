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

  <n-spin v-if="loading" :description="$t('common.loading')" class="centered-spin" />

  <div v-else-if="error" class="content-block">
    <h1>Oops... {{ $t('errors.error') }}!</h1>
    <i class="translucent">{{ $t('account.profileNotFound', { usernameOrId }) }}</i>
  </div>

  <div v-else-if="user && !error" class="content-block">
    <n-thing :content-indented="state.vw >= 900">
      <template #avatar>
        <user-avatar :username="user.username" :avatar-url="user.avatarUrl" :size="64" />
      </template>

      <template #header>
        <user-thing-header :user="user" />
      </template>

      <n-button
        v-if="auth.user && user.id !== auth.user.id && user.isActive"
        type="primary"
        class="my-md"
        @click="() => userMessages.openConversation(user?.id || '?')"
      >
        <template #icon>
          <n-icon :component="MessageIcon" />
        </template>
        {{
          $t('account.messages.btnSendMessageToUser', {
            username: user.name ?? `@${user.username}`,
          })
        }}
      </n-button>

      <p v-if="user.bio" class="pre-wrap">
        {{ user.bio }}
      </p>
      <p v-else class="translucent text-small i">
        {{ $t('account.profileNoBio') }}
      </p>
    </n-thing>
  </div>
</template>
