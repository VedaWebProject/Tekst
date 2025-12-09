<script setup lang="ts">
import { ArrowBackIcon, ArrowForwardIcon, ClearIcon, LogoutIcon } from '@/icons';
import { useWindowSize } from '@vueuse/core';
import { NButton, NFlex, NIcon, NPopover, type PopoverInst } from 'naive-ui';
import { computed, nextTick, ref, watch } from 'vue';

type TourStep = {
  key: string;
  title?: string;
  content?: string;
  before?: () => Promise<void>;
  after?: () => Promise<void>;
}

type InternalTourStep = TourStep & {
  index: number;
}

const props = withDefaults(
  defineProps<{
    steps?: TourStep[];
  }>(),
  {
    steps: () => [
      {
        key: 'header',
        title: 'The Page Header!',
        content: "Now this is a rainbow! Look at it! 🌈",
      },
      {
        key: 'footer',
        title: 'The Page Footer!',
        content: "UUnder construction! 🚧",
      },
    ]
  }
);

const { width: windowWidth, height: windowHeight } = useWindowSize({ type: 'visual' });
watch([windowWidth, windowHeight], end);

const tourSteps = computed<InternalTourStep[]>(() => props.steps.map((s, i) => ({...s, index: i})));
const step = ref<InternalTourStep>();
const show = ref(false);
const popRef = ref<PopoverInst>();
const targetMaskRef = ref<HTMLElement>();

async function runStep(offset: number = 1){
  await step.value?.after?.();
  step.value = step.value ? tourSteps.value[step.value.index + offset] : tourSteps.value[0];
  const targetEl = step.value ? document.querySelector(`[data-tour-key="${step.value.key}"]`) : undefined;
  if (!targetEl || !targetMaskRef.value){
    end();
    return;
  };
  await step.value.before?.();
  targetEl.scrollIntoView();
  targetMaskRef.value.style.top = targetEl.getBoundingClientRect().top + "px";
  targetMaskRef.value.style.left = targetEl.getBoundingClientRect().left + "px";
  targetMaskRef.value.style.width = targetEl.getBoundingClientRect().width + "px";
  targetMaskRef.value.style.height = targetEl.getBoundingClientRect().height + "px";
  popRef.value?.syncPosition();
}

function start(){
  document.body.style.height = '100%';
  document.body.style.overflow = 'hidden';
  show.value = true;
  nextTick(runStep);
}

function end(){
  step.value = undefined;
  document.body.style.height = 'initial';
  document.body.style.overflow = 'initial';
  show.value = false;
  window.scrollTo(0, 0);
}

defineExpose({ start, end });
</script>

<template>
  <template v-if="show">
    <div id="tour-click-blocker"></div>
    <div id="tour-overlay" @click="end"></div>
    <n-popover ref="popRef" trigger="manual" show :to="false" style="z-index: 1851;">
      <template #trigger>
        <div ref="targetMaskRef" id="tour-target-mask"></div>
      </template>
      <template #header>
        <n-flex justify="space-between" align="center">
          <b>{{ step?.title || '' }}</b>
          <n-button text size="small" @click="() => end()">
            <template #icon>
              <n-icon :component="ClearIcon"/>
            </template>
          </n-button>
        </n-flex>
      </template>
      <template v-if="step?.content" #default>
        <div id="tour-content">
          {{ step.content }}
        </div>
      </template>
      <template v-if="step" #footer>
        <n-flex justify="space-between" align="center">
          <n-button type="primary" size="small" :disabled="step.index <= 0" @click="() => runStep(-1)">
            <template #icon>
              <n-icon :component="ArrowBackIcon"/>
            </template>
          </n-button>
          <n-button type="primary" size="small" @click="() => runStep()">
            <template #icon>
              <n-icon v-if="step.index < tourSteps.length -1" :component="ArrowForwardIcon"/>
              <n-icon v-else :component="LogoutIcon"/>
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
  top: 0;
  left: 0;
  width: 0;
  height: 0;
  z-index: 1850;
  overscroll-behavior: contain;
  box-shadow: 0 0 0 9999px #0005;
  border-radius: var(--border-radius);
}

#tour-content {
  width: 320px;
  max-width: min(90vw, 512px);
  max-height: 60vh;
}
</style>
