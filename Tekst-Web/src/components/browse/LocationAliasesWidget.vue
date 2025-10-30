<script setup lang="ts">
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import env from '@/env';
import { NFlex } from 'naive-ui';

defineProps<{
  locationId: string;
  textSlug?: string;
  aliases?: string[];
}>();

const baseUrl = `${origin}/${env.WEB_PATH_STRIPPED}`.replace(/\/+$/, '');
</script>

<template>
  <n-flex align="center" class="my-lg">
    <template v-if="!!aliases?.length">
      <copy-to-clipboard-button
        v-for="alias in aliases"
        :key="alias"
        tertiary
        size="tiny"
        :text="`${baseUrl}/bookmark/${locationId}/${textSlug || 'unknown'}/${alias}`"
        :title="$t('browse.location.aliasesTip')"
        show-msg
      >
        {{ alias }}
      </copy-to-clipboard-button>
    </template>
    <copy-to-clipboard-button
      v-else
      tertiary
      size="tiny"
      :text="`${baseUrl}/bookmark/${locationId}/${textSlug || 'unknown'}`"
      :title="$t('browse.location.genericPermalinkTip')"
      show-msg
    >
      {{ $t('browse.location.shareLocUrl') }}
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
