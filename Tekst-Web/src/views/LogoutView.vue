<script setup lang="ts">
import { useAuthStore } from '@/stores';
import { NSpin } from 'naive-ui';
import { onMounted } from 'vue';
const auth = useAuthStore();

onMounted(() => {
  auth.logout();
});
</script>

<template>
  <n-spin class="centered-spinner my-lg" />
</template>
