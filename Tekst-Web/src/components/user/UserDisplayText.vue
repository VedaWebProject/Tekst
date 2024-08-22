<script setup lang="ts">
import type { UserReadPublic } from '@/api';

defineProps<{
  user: UserReadPublic & Record<string, any>;
}>();
</script>

<template>
  <span>
    <span v-if="user.name" class="mr-sm">{{ user.name }}</span>
    <span v-if="user.affiliation && user.name" class="mr-sm text-small">
      ({{ user.affiliation }})
    </span>
    <span v-if="!user.name">@{{ user.username }}</span>
    <span v-if="user.affiliation && !user.name" class="ml-sm"> ({{ user.affiliation }}) </span>
  </span>
</template>
