<script setup lang="ts">
import type { UserReadPublic } from '@/api';

defineProps<{
  user: UserReadPublic & Record<string, any>;
}>();
</script>

<template>
  <span>
    <span v-if="user.name" style="margin-right: 0.25rem">{{ user.name }}</span>
    <span v-if="user.affiliation && user.name" style="margin-right: 0.25rem; font-size: 85%"
      >({{ user.affiliation }})</span
    >
    <span v-if="!user.name">@{{ user.username }}</span>
    <span v-if="user.affiliation && !user.name" style="margin-left: 0.25rem"
      >({{ user.affiliation }})</span
    >
  </span>
</template>
