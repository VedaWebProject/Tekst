<script setup lang="ts">
import GenericModal from '@/components/generic/GenericModal.vue';
import type { HelpText } from '@/composables/help';
import { useHelp } from '@/composables/help';
import { $t } from '@/i18n';
import { NButton, NIcon, NSpin } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { computed, ref } from 'vue';

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

const emit = defineEmits(['click']);

const { getHelpText } = useHelp();
const showModal = ref(false);
const loading = ref(false);
const helpText = ref<HelpText>();

const buttonStyle = computed(() => ({
  alignSelf: 'center',
  verticalAlign: 'center',
  marginLeft: props.gapLeft ? 'var(--gap-sm)' : undefined,
  marginRight: props.gapRight ? 'var(--gap-sm)' : undefined,
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
  emit('click');
  loadHelp();
  showModal.value = true;
}
</script>

<template>
  <n-button
    secondary
    circle
    color="var(--primary-color)"
    :size="size"
    :title="$t('common.help')"
    :focusable="false"
    :style="buttonStyle"
    @click.stop.prevent="handleHelpButtonClick"
  >
    <template #icon>
      <n-icon :component="QuestionMarkIcon" />
    </template>
  </n-button>

  <generic-modal
    v-model:show="showModal"
    width="wide"
    :title="$t('common.help')"
    :icon="QuestionMarkIcon"
    heading-level="3"
    @after-leave="handleClose"
  >
    <n-spin
      :show="loading"
      :delay="100"
      :description="$t('common.loading')"
      content-style="width: 100%;"
      class="centered-spinner"
      style="padding: 0"
    >
      <div v-if="helpText" v-html="helpText.content"></div>
      <div v-else-if="!loading">{{ $t('help.errorNotFound') }}</div>
    </n-spin>
  </generic-modal>
</template>
