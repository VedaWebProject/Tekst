<script setup lang="ts">
import { useProfile } from '@/profile';
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const username = computed(() =>
  route.name === 'user' && route.params.username ? String(route.params.username) : undefined
);
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
  <div v-else class="content-block">
    <h1>Oops... {{ $t('errors.error') }}!</h1>
    {{ $t('user.profileNotFound', { username }) }}
  </div>
</template>
