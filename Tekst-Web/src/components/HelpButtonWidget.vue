<script setup lang="ts">
import { computed, ref } from 'vue';
import { NButton, NIcon, NSpin } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { $t } from '@/i18n';
import { useHelp } from '@/composables/help';
import type { HelpText } from '@/composables/help';
import GenericModal from '@/components/generic/GenericModal.vue';

import { QuestionMarkIcon } from '@/icons';

const props = withDefaults(
  defineProps<{
    helpKey: string;
    size?: Size;
    gapLeft?: boolean;
    gapRight?: boolean;
  }>(),
  {
    size: 'tiny',
  }
);

const { getHelpText } = useHelp();
const showModal = ref(false);
const loading = ref(false);
const helpText = ref<HelpText>();

const buttonStyle = computed(() => ({
  alignSelf: 'center',
  verticalAlign: 'center',
  marginLeft: props.gapLeft ? 'var(--content-gap)' : undefined,
  marginRight: props.gapRight ? 'var(--content-gap)' : undefined,
}));

async function loadHelp() {
  loading.value = true;
  try {
    helpText.value = await getHelpText(props.helpKey);
  } catch {
    helpText.value = undefined;
  }
  loading.value = false;
}

async function handleClose() {
  helpText.value = undefined;
}

async function handleHelpButtonClick() {
  loadHelp();
  showModal.value = true;
}
</script>

<template>
  <n-button
    secondary
    circle
    color="var(--accent-color)"
    :size="size"
    :title="$t('help.tipHelpButton')"
    :focusable="false"
    :style="buttonStyle"
    @click="handleHelpButtonClick"
  >
    <template #icon>
      <n-icon :component="QuestionMarkIcon" />
    </template>
  </n-button>

  <generic-modal
    v-model:show="showModal"
    width="wide"
    :title="$t('help.help')"
    :icon="QuestionMarkIcon"
    heading-level="3"
    @after-leave="handleClose"
  >
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div v-if="helpText" v-html="helpText.content"></div>
    <n-spin
      v-else-if="loading"
      :description="$t('general.loading')"
      style="width: 100%; display: flex; justify-content: center"
    />
    <div v-else>{{ $t('help.errorNotFound') }}</div>
  </generic-modal>
</template>
