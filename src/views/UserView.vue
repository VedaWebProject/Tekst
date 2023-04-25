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
  <div v-if="user && !error" class="content-block">
    <h1>{{ $t('user.profileHeading', { username }) }}</h1>
    <ul>
      <li v-if="user?.username">
        <b>{{ $t('register.labels.username') }}:</b> {{ user.username }}
      </li>
      <li v-if="user?.email">
        <b>{{ $t('register.labels.email') }}:</b> {{ user.email }}
      </li>
      <li v-if="user?.firstName">
        <b>{{ $t('register.labels.firstName') }}:</b> {{ user.firstName }}
      </li>
      <li v-if="user?.lastName">
        <b>{{ $t('register.labels.lastName') }}:</b> {{ user.lastName }}
      </li>
      <li v-if="user?.affiliation">
        <b>{{ $t('register.labels.affiliation') }}:</b> {{ user.affiliation }}
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
    {{ $t('user.profileNotFound', { username }) }}
  </div>
</template>
