<script setup lang="ts">
import { UserIcon } from '@/icons';
import { NAvatar, NIcon } from 'naive-ui';
import type { Size } from 'naive-ui/es/avatar/src/interface';
import nyf from 'notyourface';
import { computed, h } from 'vue';

const nyfOptions: Parameters<(typeof nyf)['dataURI']>[0] = {
  complexity: 4,
  cache: 512,
  size: 128,
};

const props = defineProps<{
  username?: string;
  avatarUrl?: string | null;
  size?: Size;
}>();

const avatar = computed(
  () =>
    props.avatarUrl ||
    (props.username ? nyf.dataURI({ ...nyfOptions, seed: props.username }) : undefined)
);
</script>

<template>
  <n-avatar
    round
    :src="avatar"
    :render-fallback="() => h(NIcon, { component: UserIcon })"
    :size="size"
    object-fit="cover"
    color="var(--primary-color-fade4)"
    :style="{
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'var(--main-bg-color)',
      flexShrink: 0,
    }"
  />
</template>
