<script setup lang="ts">
import { useAuthStore, useStateStore } from '@/stores';
import { watchOnce } from '@vueuse/core';
import { NSpin } from 'naive-ui';
import { nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const state = useStateStore();
const auth = useAuthStore();
const router = useRouter();

onMounted(() => {
  if (!state.pf?.security.closedMode || !!auth.user) {
    router.push({ name: 'home' });
    return;
  }
  nextTick(() => {
    auth.showLoginModal(undefined, undefined, false);
    watchOnce(
      () => auth.loginModalState.show,
      (showLoginModal) => {
        if (!showLoginModal) {
          router.push({ name: 'home' });
        }
      }
    );
  });
});
</script>

<template>
  <n-spin class="centered-spinner my-lg"></n-spin>
</template>
