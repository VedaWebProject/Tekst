<script setup lang="ts">
import { UserIcon } from '@/icons';
import { NAvatar, NIcon } from 'naive-ui';
import type { Size } from 'naive-ui/es/avatar/src/interface';
import { h, type Component } from 'vue';

defineProps<{
  avatarUrl?: string;
  size?: Size;
  fallbackIcon?: Component;
}>();
</script>

<template>
  <n-avatar
    round
    :src="avatarUrl || undefined"
    :render-fallback="() => h(NIcon, { component: fallbackIcon || UserIcon })"
    :size="size"
    object-fit="cover"
    color="var(--primary-color-fade4)"
    :style="{
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'var(--main-bg-color)',
      flexShrink: 0,
    }"
  >
    <n-icon v-if="!avatarUrl" :component="fallbackIcon || UserIcon" :size="size" />
  </n-avatar>
</template>
