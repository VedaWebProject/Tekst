<script setup lang="ts">
import { useAuthStore } from '@/stores';
import { NSpin } from 'naive-ui';
const auth = useAuthStore();
auth.logout();
</script>

<template>
  <n-spin size="large" class="centered-spinner my-lg" />
</template>
