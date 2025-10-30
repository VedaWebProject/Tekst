<script setup lang="ts">
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import env from '@/env';
import { $t } from '@/i18n';
import { NFlex } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  locationId: string;
  textSlug?: string;
  aliases?: string[];
}>();

const baseUrl = `${origin}/${env.WEB_PATH_STRIPPED}`.replace(/\/+$/, '');
const data = computed(
  () =>
    props.aliases?.map((alias) => ({
      text: alias,
      tip: $t('browse.location.aliasesTip'),
      url: encodeURI(
        `${baseUrl}/bookmark/${props.locationId}/${props.textSlug || 'unknown'}/${alias}`
      ),
    })) || [
      {
        text: $t('browse.location.shareLocUrl'),
        tip: $t('browse.location.genericPermalinkTip'),
        url: encodeURI(`${baseUrl}/bookmark/${props.locationId}/${props.textSlug || 'unknown'}`),
      },
    ]
);
</script>

<template>
  <n-flex align="center" class="my-lg">
    <copy-to-clipboard-button
      v-for="(alias, index) in data"
      :key="`alias_${index}`"
      tertiary
      size="tiny"
      :text="alias.url"
      :title="alias.tip"
      show-msg
    >
      {{ alias.text }}
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
