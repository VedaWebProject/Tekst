<script setup lang="ts">
import { useAuthStore } from '@/stores';
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const auth = useAuthStore();

onMounted(() => {
  router.push({ name: 'home' });
  auth.showLoginModal(undefined, { name: 'accountProfile' }, false);
});
</script>

<template>...</template>
