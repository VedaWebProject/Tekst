<script setup lang="ts">
import { useAuthStore } from '@/stores';
import { NSpin } from 'naive-ui';
const auth = useAuthStore();
auth.logout();
</script>

<template>
  <n-spin size="large" class="centered-spinner" style="margin: var(--layout-gap) 0" />
</template>
