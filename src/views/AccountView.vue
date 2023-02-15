<script setup lang="ts">
import { useUiDataStore, useAuthStore } from '@/stores';

const ui = useUiDataStore();
const auth = useAuthStore();
const { email, firstName, lastName } = { ...auth.user };
</script>

<template>
  <h1>
    {{ firstName }}'{{ !firstName?.toLowerCase().endsWith('s') && 's' }}
    {{ ui.get('platform.title') }} Account
  </h1>
  <ul>
    <li><b>Email:</b> {{ email }}</li>
    <li><b>Name:</b> {{ firstName }} {{ lastName }}</li>
  </ul>
</template>
