<script setup lang="ts">
import type { UserReadPublic } from '@/api';

const props = defineProps<{
  user: UserReadPublic & Record<string, any>;
}>();

const fullName = (props.user.firstName + ' ' + (props.user.lastName || ''))?.trim();
const personal = [fullName, props.user.affiliation].filter((s) => s).join(', ');
const username = `@${props.user.username}`;
</script>

<template>
  <span v-if="personal" style="padding-right: 0.25rem">{{ personal }}</span>
  <span :style="personal ? 'opacity: 0.5' : undefined">{{ username }}</span>
</template>
