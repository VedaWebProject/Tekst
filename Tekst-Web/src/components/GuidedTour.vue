<script setup lang="ts">
import { $t } from '@/i18n';
import { ArrowBackIcon, ArrowForwardIcon, CheckIcon, ClearIcon, TourIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { delay } from '@/utils';
import { useWindowSize } from '@vueuse/core';
import { NButton, NFlex, NIcon, NPopover, type PopoverInst } from 'naive-ui';
import { computed, nextTick, onMounted, ref, watch } from 'vue';

type TourStep = {
  key: string;
  title?: string;
  content?: string;
  before?: () => Promise<void>;
  after?: () => Promise<void>;
};

type InternalTourStep = TourStep & {
  index: number;
};

const props = withDefaults(
  defineProps<{
    steps?: TourStep[];
  }>(),
  {
    steps: () => [
      {
        key: 'header',
        title: 'The Page Header!',
        content: $t('errors.loginUserNotVerified'),
        before: async () => console.log('BEFORE STEP 1!'),
        after: async () => console.log('AFTER STEP 1!'),
      },
      {
        key: 'footer',
        title: 'The Page Footer!',
        content: $t('errors.logoutAfter401'),
        before: async () => console.log('BEFORE STEP 2!'),
        after: async () => console.log('AFTER STEP 2!'),
      },
    ],
  }
);

const state = useStateStore();

const { width: windowWidth, height: windowHeight } = useWindowSize({ type: 'visual' });
watch([windowWidth, windowHeight], end);

const tourSteps = computed<InternalTourStep[]>(() =>
  props.steps.map((s, i) => ({ ...s, index: i }))
);
const step = ref<InternalTourStep>();
const show = ref(false);
const popoverShow = ref(false);
const popRef = ref<PopoverInst>();
const targetMaskRef = ref<HTMLElement>();

async function nextStep(offset: number = 1) {
  popoverShow.value = false;
  await step.value?.after?.();
  if (step.value) await delay(100);
  step.value = step.value ? tourSteps.value[step.value.index + offset] : tourSteps.value[0];
  const targetEl = step.value
    ? document.querySelector(`[data-tour-key="${step.value.key}"]`)
    : undefined;
  if (!targetEl || !targetMaskRef.value) {
    end();
    return;
  }
  targetMaskRef.value.style.visibility = 'hidden';
  await step.value.before?.();
  targetEl.scrollIntoView();
  targetMaskRef.value.style.top = targetEl.getBoundingClientRect().top + 'px';
  targetMaskRef.value.style.left = targetEl.getBoundingClientRect().left + 'px';
  targetMaskRef.value.style.width = targetEl.getBoundingClientRect().width + 'px';
  targetMaskRef.value.style.height = targetEl.getBoundingClientRect().height + 'px';
  targetMaskRef.value.style.visibility = 'visible';
  popRef.value?.syncPosition();
  popoverShow.value = true;
}

async function start() {
  document.body.style.height = '100%';
  document.body.style.overflow = 'hidden';
  show.value = true;
  await delay(100);
  nextTick(nextStep);
}

async function end() {
  popoverShow.value = false;
  await step.value?.after?.();
  await delay(200);
  step.value = undefined;
  document.body.style.height = 'initial';
  document.body.style.overflow = 'initial';
  show.value = false;
  window.scrollTo(0, 0);
}

defineExpose({ start, end });
onMounted(end);
</script>

<template>
  <template v-if="show">
    <div id="tour-click-blocker"></div>
    <div id="tour-overlay" @click="end"></div>
    <n-popover
      ref="popRef"
      trigger="manual"
      :show="popoverShow"
      :to="false"
      style="z-index: 1851"
      arrow-point-to-center
    >
      <template #trigger>
        <div ref="targetMaskRef" id="tour-target-mask" @click="end"></div>
      </template>
      <template #header>
        <n-flex align="center" size="small">
          <n-icon :component="TourIcon" />
          <b style="flex: 2">{{ step?.title || '' }}</b>
          <span v-if="step">{{ step.index + 1 }}/{{ tourSteps.length }}</span>
        </n-flex>
      </template>
      <template v-if="step?.content" #default>
        <div id="tour-step-content">
          {{ step.content }}
        </div>
      </template>
      <template v-if="step" #footer>
        <n-flex justify="space-between" align="center">
          <n-button
            secondary
            type="primary"
            size="small"
            :disabled="step.index <= 0"
            @click="() => nextStep(-1)"
          >
            <template #icon>
              <n-icon :component="ArrowBackIcon" />
            </template>
            <template v-if="!state.smallScreen">
              {{ $t('help.tour.prev') }}
            </template>
          </n-button>
          <n-button v-if="step.index < tourSteps.length - 1" secondary size="small" @click="end">
            <template #icon>
              <n-icon :component="ClearIcon" />
            </template>
            <template v-if="!state.smallScreen">
              {{ $t('common.close') }}
            </template>
          </n-button>
          <n-button type="primary" size="small" @click="() => nextStep()" icon-placement="right">
            <template #icon>
              <n-icon v-if="step.index < tourSteps.length - 1" :component="ArrowForwardIcon" />
              <n-icon v-else :component="CheckIcon" />
            </template>
            <template v-if="!state.smallScreen">
              <template v-if="step.index < tourSteps.length - 1">
                {{ $t('help.tour.next') }}
              </template>
              <template v-else>
                {{ $t('common.ok') }}
              </template>
            </template>
          </n-button>
        </n-flex>
      </template>
    </n-popover>
  </template>
</template>

<style scoped>
#tour-click-blocker {
  position: fixed;
  inset: 0px;
  pointer-events: none;
  visibility: hidden;
}

#tour-overlay {
  position: fixed;
  inset: 0px;
  z-index: 1849;
  overflow: hidden;
  overscroll-behavior: contain;
}

#tour-target-mask {
  position: fixed;
  visibility: hidden;
  top: 0;
  left: 0;
  width: 0;
  height: 0;
  z-index: 1850;
  overscroll-behavior: contain;
  box-shadow: 0 0 0 9999px #0006;
  border-radius: var(--border-radius);
  transition: visibility 0.2s ease-in-out;
}

#tour-step-content {
  width: 512px;
  max-width: min(90vw, 768px);
  max-height: 60vh;
}
</style>
