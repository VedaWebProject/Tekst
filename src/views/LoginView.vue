<script setup lang="ts">
import { useUiDataStore, useAuthStore } from '@/stores';
import { NInput, NSpace, NButton } from 'naive-ui';
import { ref } from 'vue';

const ui = useUiDataStore();
const auth = useAuthStore();
const username = ref('');
const password = ref('');
</script>

<template>
  <h1>{{ ui.get('platform.title') }} Login</h1>
  <n-space vertical>
    <n-input v-model:value="username" type="text" placeholder="Username" />
    <n-input v-model:value="password" type="password" placeholder="Password" />
    <n-button @click="() => auth.login(username, password)" type="primary"> Login </n-button>
  </n-space>
</template>
