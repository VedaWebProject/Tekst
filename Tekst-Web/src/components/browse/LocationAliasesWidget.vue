<script setup lang="ts">
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import env from '@/env';
import { NFlex } from 'naive-ui';

defineProps<{
  textSlug: string;
  aliases?: string[];
}>();

const baseUrl = `${origin}/${env.WEB_PATH_STRIPPED}`.replace(/\/+$/, '');
</script>

<template>
  <n-flex align="center" class="my-lg">
    <copy-to-clipboard-button
      v-for="alias in aliases"
      :key="alias"
      tertiary
      size="tiny"
      :text="`${baseUrl}/bookmark/${textSlug}/${alias}`"
      :title="$t('browse.location.aliasesTip')"
      show-msg
    >
      {{ alias }}
    </copy-to-clipboard-button>
  </n-flex>
</template>

<style scoped>
.loc-alias-tag {
  cursor: pointer;
}

.loc-alias-tag:hover {
  background-color: var(--main-bg-color);
}
</style>
