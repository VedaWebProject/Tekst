<script setup lang="ts">
import { ref } from 'vue';
import { NModal, NButton, NIcon, NSpin } from 'naive-ui';

import QuestionMarkFilled from '@vicons/material/QuestionMarkFilled';
import type { Size } from 'naive-ui/es/button/src/interface';
import { $t } from '@/i18n';
import { useHelp, type HelpText } from '@/help';

const props = withDefaults(
  defineProps<{
    helpKey: string;
    size?: Size;
  }>(),
  {
    size: 'tiny',
  }
);

const { getHelpText } = useHelp();
const showModal = ref(false);
const loading = ref(false);
const helpText = ref<HelpText>();

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
    style="display: inline-flex; align-self: center; vertical-align: center"
    @click="handleHelpButtonClick"
  >
    <template #icon>
      <n-icon :component="QuestionMarkFilled" />
    </template>
  </n-button>

  <n-modal
    v-model:show="showModal"
    display-directive="if"
    preset="card"
    class="tekst-modal-wide"
    size="medium"
    :bordered="false"
    :auto-focus="false"
    :closable="true"
    to="#app-container"
    :title="$t('help.help')"
    embedded
    @after-leave="handleClose"
  >
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div v-if="helpText" v-html="helpText.content"></div>
    <n-spin
      v-else-if="loading"
      :description="$t('init.loading')"
      style="width: 100%; display: flex; justify-content: center"
    />
    <div v-else>{{ $t('help.errorNotFound') }}</div>
  </n-modal>
</template>
