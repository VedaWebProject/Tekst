<script setup lang="ts">
import { useProfile } from '@/fetchers';
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { NSpin } from 'naive-ui';
import { useAuthStore } from '@/stores';
import IconHeading from '@/components/typography/IconHeading.vue';

import PersonFilled from '@vicons/material/PersonFilled';

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
  <IconHeading level="1" :icon="PersonFilled">
    {{ $t('account.profileHeading', { username }) }}
  </IconHeading>

  <div v-if="user && !error" class="content-block">
    <ul>
      <template v-for="(value, key) in user" :key="key">
        <li v-if="key !== 'id'">
          <b>{{ $t(`models.user.${key}`) }}: </b>
          <span v-if="value">{{ value }}</span>
          <span v-else style="opacity: 0.5; font-style: italic">{{
            $t('account.profileFieldNotPublic')
          }}</span>
        </li>
      </template>
    </ul>
  </div>

  <n-spin v-else-if="!error" :description="$t('init.loading')" />

  <div v-else class="content-block">
    <h1>Oops... {{ $t('errors.error') }}!</h1>
    {{ $t('account.profileNotFound', { username }) }}
  </div>
</template>
