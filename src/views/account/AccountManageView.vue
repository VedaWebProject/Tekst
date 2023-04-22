<script setup lang="ts">
import { useAuthStore } from '@/stores';

const auth = useAuthStore();
</script>

<template>
  <h2>{{ $t('user.account.headingManage') }}</h2>
  <ul>
    <li><b>Email:</b> {{ auth.user?.email }}</li>
    <li><b>Username:</b> {{ auth.user?.username }}</li>
    <li><b>Name:</b> {{ auth.user?.firstName }} {{ auth.user?.lastName }}</li>
  </ul>
</template>
