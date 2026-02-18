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
  explode?: boolean;
}>();

const baseUrl = `${origin}/${env.WEB_PATH_STRIPPED}`.replace(/\/+$/, '');
const locUrl = computed(
  () => `${baseUrl}/bookmark/${props.locationId}/${props.textSlug || 'unknown'}`
);
const locUrlEncoded = computed(() => encodeURI(locUrl.value));

const data = computed(
  () =>
    props.aliases?.map((alias) => ({
      text: alias,
      tip: $t('browse.location.aliasesTip'),
      url: encodeURI(`${locUrl.value}/${alias}`),
    })) || [
      {
        text: $t('browse.location.copyLocUrl'),
        tip: $t('browse.location.genericPermalinkTip'),
        url: locUrlEncoded.value,
      },
    ]
);
</script>

<template>
  <n-flex v-if="explode" align="center">
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
  <copy-to-clipboard-button
    v-else
    tertiary
    size="tiny"
    :text="locUrlEncoded"
    :title="$t('browse.location.genericPermalinkTip')"
    show-msg
  >
    {{ $t('browse.location.copyLocUrl') }}
  </copy-to-clipboard-button>
</template>
