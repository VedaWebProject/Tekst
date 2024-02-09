<script setup lang="ts">
import { useProfile } from '@/composables/fetchers';
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { NSpin, NThing, NIcon } from 'naive-ui';
import { useAuthStore } from '@/stores';
import IconHeading from '@/components/generic/IconHeading.vue';
import UserAvatar from '@/components/user/UserAvatar.vue';

import { AdminIcon, UserIcon } from '@/icons';

const route = useRoute();

const username = computed(() => {
  if (route.name) {
    if (route.name === 'user' && route.params.username) {
      return String(route.params.username);
    } else if (route.name === 'accountProfile') {
      const auth = useAuthStore();
      return auth.user?.username || '';
    }
  }
  return '';
});
const { user, error } = useProfile(username);
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
        <div style="display: flex; align-items: center; gap: 0.5rem">
          {{ user.name || `@${user.username}` }}
          <span v-if="user.name" class="translucent text-small n"> @{{ user.username }} </span>
          <n-icon
            v-if="user.isSuperuser"
            :component="AdminIcon"
            color="var(--accent-color)"
            :title="$t('models.user.isSuperuser')"
          />
        </div>
      </template>
      <template v-if="user.name" #description>
        {{ user.affiliation }}
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
