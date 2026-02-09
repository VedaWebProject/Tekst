<script setup lang="ts">
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import { useMessages } from '@/composables/messages';
import env from '@/env';
import { $t } from '@/i18n';
import { CopyIcon, LabelIcon } from '@/icons';
import { renderIcon } from '@/utils';
import { useClipboard } from '@vueuse/core';
import { NButton, NDropdown, NFlex, NIcon, type DropdownOption } from 'naive-ui';
import type { Type } from 'naive-ui/es/button/src/interface';
import { computed, useAttrs } from 'vue';

const props = defineProps<{
  locationId: string;
  textSlug?: string;
  aliases?: string[];
  unwrap?: boolean;
}>();

const { message } = useMessages();
const { copy, copied, isSupported } = useClipboard({ copiedDuring: 1000 });
const attrs: Record<string, unknown> = useAttrs();

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
        text: $t('browse.location.copyLocUrl'),
        tip: $t('browse.location.genericPermalinkTip'),
        url: encodeURI(`${baseUrl}/bookmark/${props.locationId}/${props.textSlug || 'unknown'}`),
      },
    ]
);

const options = computed<DropdownOption[]>(() =>
  data.value.map((alias) => ({
    label: alias.text,
    key: alias.url,
    disabled: !isSupported,
    icon: renderIcon(CopyIcon),
    props: { title: alias.tip },
  }))
);

function copyToClipboard(text?: string) {
  if (!text) return;
  copy(text);
  message.success($t('common.copiedMsg', { text }));
}
</script>

<template>
  <n-flex v-if="unwrap || options.length <= 1" align="center">
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
  <n-dropdown v-else :options="options" @select="(v) => copyToClipboard(v)">
    <n-button
      secondary
      :type="copied ? 'success' : (attrs.type as Type | undefined)"
      size="tiny"
      :title="$t('browse.location.genericPermalinkTip')"
    >
      <template #icon>
        <n-icon :component="LabelIcon" />
      </template>
      {{ $t('browse.location.copyLocUrl') }}
    </n-button>
  </n-dropdown>
</template>

<style scoped>
.loc-alias-tag {
  cursor: pointer;
}

.loc-alias-tag:hover {
  background-color: var(--main-bg-color);
}
</style>
