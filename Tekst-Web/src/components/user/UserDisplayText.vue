<script setup lang="ts">
import type { UserReadPublic } from '@/api';

defineProps<{
  user: UserReadPublic & Record<string, any>;
}>();
</script>

<template>
  <span v-if="user.name" style="margin-right: 0.25rem">{{ user.name }}</span>
  <span v-if="user.affiliation && user.name" style="margin-right: 0.25rem"
    >({{ user.affiliation }})</span
  >
  <span style="opacity: 0.75">@{{ user.username }}</span>
  <span v-if="user.affiliation && !user.name" style="margin-left: 0.25rem"
    >({{ user.affiliation }})</span
  >
</template>
