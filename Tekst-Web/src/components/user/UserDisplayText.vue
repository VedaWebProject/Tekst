<script setup lang="ts">
import type { UserReadPublic } from '@/api';

defineProps<{
  user: UserReadPublic;
}>();
</script>

<template>
  <span>
    <span v-if="user.name">{{ user.name }}</span>
    <span v-else>@{{ user.username }}</span>
    <span v-if="user.affiliation"> ({{ user.affiliation }}) </span>
  </span>
</template>
