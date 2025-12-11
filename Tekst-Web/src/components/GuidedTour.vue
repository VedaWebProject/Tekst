<script setup lang="ts">
import { $t } from '@/i18n';
import { ArrowBackIcon, ArrowForwardIcon, CheckIcon, ClearIcon, TourIcon } from '@/icons';
import { useStateStore } from '@/stores';
import steps from '@/tour';
import { delay } from '@/utils';
import { useElementBounding } from '@vueuse/core';
import { NButton, NFlex, NIcon, NPopover, type PopoverInst } from 'naive-ui';
import { computed, nextTick, ref, watchEffect, type WatchHandle } from 'vue';
import { useRouter, type RouteLocationRaw } from 'vue-router';

type InternalTourStep = {
  key: string;
  index: number;
  route?: RouteLocationRaw;
  title?: string;
  text?: string;
  before?: () => Promise<void>;
  after?: () => Promise<void>;
};

const state = useStateStore();
const router = useRouter();

const tourSteps = computed<InternalTourStep[]>(() =>
  steps.map((s, i) => ({ ...s, title: s.title?.(), text: s.text?.(), index: i }))
);
const step = ref<InternalTourStep>();
const show = ref(false);
const popoverShow = ref(false);
const popRef = ref<PopoverInst>();
const targetMaskRef = ref<HTMLElement>();
const activeElWatcher = ref<WatchHandle>();

function lockTargetEl(el: HTMLElement, maskEl: HTMLElement) {
  activeElWatcher.value?.stop();
  const {
    width: w,
    height: h,
    x,
    y,
  } = useElementBounding(el, {
    updateTiming: 'sync',
    windowResize: true,
    windowScroll: true,
    immediate: true,
    reset: true,
  });
  activeElWatcher.value = watchEffect(async () => {
    await nextTick();
    maskEl.style.opacity = '0';
    el.scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });
    maskEl.style.top = y.value - 16 + 'px';
    maskEl.style.left = x.value - 16 + 'px';
    maskEl.style.width = w.value + 32 + 'px';
    maskEl.style.height = h.value + 32 + 'px';
    maskEl.style.opacity = '1';
    popRef.value?.syncPosition();
  });
}

async function nextStep(offset: number = 1) {
  popoverShow.value = false;
  await delay(200); // give transitions some time to finish
  if (!targetMaskRef.value) return end();
  await step.value?.after?.();
  step.value = step.value ? tourSteps.value[step.value.index + offset] : tourSteps.value[0];
  if (!step.value) return end();
  const targetRouteResolved = step.value.route ? router.resolve(step.value.route) : null;
  if (targetRouteResolved && router.currentRoute.value.name !== targetRouteResolved.name) {
    targetMaskRef.value.style.opacity = '0';
    await router.replace(targetRouteResolved);
  }
  await step.value.before?.();
  let targetEl: HTMLElement | undefined;
  // find and lock target element
  for (let i = 0; i < 50; i++) {
    // we're giving this 5 seconds max. to account for slow loading of nested components
    targetEl =
      (document.querySelector(`[data-tour-key="${step.value.key}"]`) as HTMLElement) || undefined;
    if (targetEl) {
      lockTargetEl(targetEl, targetMaskRef.value);
      popoverShow.value = true;
      return;
    }
    await delay(100);
  }
  return end();
}

async function start() {
  document.body.style.height = '100%';
  document.body.style.overflow = 'hidden';
  if (targetMaskRef.value) targetMaskRef.value.style.opacity = '0';
  show.value = true;
  nextTick(nextStep);
}

async function end() {
  step.value?.after?.();
  activeElWatcher.value?.stop();
  activeElWatcher.value = undefined;
  popoverShow.value = false;
  if (targetMaskRef.value) targetMaskRef.value.style.opacity = '0';
  await delay(200);
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
    <n-popover ref="popRef" trigger="manual" :show="popoverShow" style="z-index: 1851">
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
      <template v-if="step?.text" #default>
        <div id="tour-step-content">
          {{ step.text }}
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
              {{ $t('tour.prev') }}
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
                {{ $t('tour.next') }}
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
}

#tour-target-mask {
  position: fixed;
  opacity: 0;
  top: 0;
  left: 0;
  width: 0;
  height: 0;
  z-index: 1850;
  box-shadow:
    0 0 8px 2px var(--base-color),
    inset 0 0 8px 2px var(--base-color),
    0 0 0 9999px #0007;
  border-radius: 8px;
  transition: opacity 0.2s ease-in-out;
}

#tour-step-content {
  width: 512px;
  max-width: min(90vw, 768px);
  max-height: 60vh;
}
</style>
