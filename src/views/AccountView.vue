<script setup lang="ts">
import { usePlatformStore, useAuthStore } from '@/stores';

const pf = usePlatformStore();
const auth = useAuthStore();
</script>

<template>
  <h1>
    {{ auth.user?.firstName }}'{{ !auth.user?.firstName.toLowerCase().endsWith('s') && 's' }}
    {{ pf.get('info.platformName') }} Account
  </h1>
  <ul>
    <li><b>Email:</b> {{ auth.user?.email }}</li>
    <li><b>Name:</b> {{ auth.user?.firstName }} {{ auth.user?.lastName }}</li>
  </ul>
</template>
