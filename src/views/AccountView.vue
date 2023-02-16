<script setup lang="ts">
import { useUiDataStore, useAuthStore } from '@/stores';

const ui = useUiDataStore();
const auth = useAuthStore();
</script>

<template>
  <h1>
    {{ auth.user?.firstName }}'{{ !auth.user?.firstName.toLowerCase().endsWith('s') && 's' }}
    {{ ui.get('platform.title') }} Account
  </h1>
  <ul>
    <li><b>Email:</b> {{ auth.user?.email }}</li>
    <li><b>Name:</b> {{ auth.user?.firstName }} {{ auth.user?.lastName }}</li>
  </ul>
</template>
