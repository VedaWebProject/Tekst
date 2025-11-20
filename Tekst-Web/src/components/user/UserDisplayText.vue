<script setup lang="ts">
import type { UserReadPublic } from '@/api';

withDefaults(
  defineProps<{
    user: UserReadPublic;
    showAffiliation?: boolean;
  }>(),
  {
    showAffiliation: true,
  }
);
</script>

<template>
  <span>
    <span v-if="user.name">{{ user.name }}</span>
    <span v-else>@{{ user.username }}</span>
    <span v-if="showAffiliation && user.affiliation"> ({{ user.affiliation }}) </span>
  </span>
</template>
