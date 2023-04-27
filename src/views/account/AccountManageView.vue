<script setup lang="ts">
import { useAuthStore } from '@/stores';

const auth = useAuthStore();
</script>

<template>
  <h1>{{ $t('user.account.headingManage') }}</h1>
  <div class="content-block">
    <ul>
      <li><b>Email:</b> {{ auth.user?.email }}</li>
      <li><b>Username:</b> {{ auth.user?.username }}</li>
      <li><b>Name:</b> {{ auth.user?.firstName }} {{ auth.user?.lastName }}</li>
    </ul>
  </div>
</template>
