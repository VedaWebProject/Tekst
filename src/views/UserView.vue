<script setup lang="ts">
import { useProfile } from '@/fetchers';
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { NSpin } from 'naive-ui';
import { useAuthStore } from '@/stores';

const route = useRoute();
const username = computed(() => {
  if (route.name) {
    if (route.name === 'user' && route.params.username) {
      return String(route.params.username);
    } else if (route.name === 'accountProfile') {
      const auth = useAuthStore();
      return auth.user?.username;
    }
  }
  return null;
});
const { user, error } = useProfile(username);
</script>

<template>
  <h1>{{ $t('account.profileHeading', { username }) }}</h1>
  <div v-if="user && !error" class="content-block">
    <ul>
      <li v-for="(value, key) in user" :key="key">
        <b>{{ $t(`models.user.${key}`) }}: </b>
        <span v-if="value">{{ value }}</span>
        <span v-else style="opacity: 0.5; font-style: italic">{{
          $t('account.profileFieldNotPublic')
        }}</span>
      </li>
    </ul>
  </div>

  <n-spin v-else-if="!error">
    <template #description>
      {{ $t('init.loading') }}
    </template>
  </n-spin>

  <div v-else class="content-block">
    <h1>Oops... {{ $t('errors.error') }}!</h1>
    {{ $t('account.profileNotFound', { username }) }}
  </div>
</template>
