<script setup lang="ts">
import GenericModal from '@/components/generic/GenericModal.vue';
import type { HelpText } from '@/composables/help';
import { useHelp } from '@/composables/help';
import { $t } from '@/i18n';
import { ErrorIcon, QuestionMarkIcon } from '@/icons';
import { NButton, NEmpty, NIcon, NSpin } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { computed, ref } from 'vue';

const props = withDefaults(
  defineProps<{
    helpKey: string;
    size?: Size;
    gapLeft?: boolean;
    gapRight?: boolean;
    link?: string;
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
  // unset current help text
  helpText.value = undefined;
  // remove hash from url
  window.location.hash = '';
}

async function handleHelpButtonClick() {
  emit('click');
  loadHelp();
  showModal.value = true;
}
</script>

<template>
  <a v-if="props.link" v-bind="$attrs" @click.stop.prevent="handleHelpButtonClick">
    {{ props.link }}
  </a>
  <n-button
    v-else
    v-bind="$attrs"
    secondary
    circle
    color="var(--primary-color)"
    :size="size"
    :title="$t('help.help')"
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
    :title="$t('help.help')"
    :icon="QuestionMarkIcon"
    heading-level="3"
    @after-leave="handleClose"
  >
    <n-spin
      :show="loading"
      :delay="100"
      :description="$t('common.loading')"
      content-style="width: 100%;"
      class="centered-spin"
      style="padding: 0"
    >
      <div v-if="helpText" v-html="helpText.content"></div>
      <n-empty v-else-if="!loading" :description="$t('errors.notFound')">
        <template #icon>
          <n-icon :component="ErrorIcon" />
        </template>
      </n-empty>
    </n-spin>
  </generic-modal>
</template>
