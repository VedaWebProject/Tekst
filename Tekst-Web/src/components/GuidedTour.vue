<script setup lang="ts">
import { $t } from '@/i18n';
import { ArrowBackIcon, ArrowForwardIcon, CheckIcon, ClearIcon, TourIcon } from '@/icons';
import { useStateStore } from '@/stores';
import steps from '@/tour';
import { delay } from '@/utils';
import { useElementBounding } from '@vueuse/core';
import { NButton, NFlex, NIcon, NPopover, type PopoverInst } from 'naive-ui';
import { computed, nextTick, ref, watch, type WatchHandle } from 'vue';
import { useRouter } from 'vue-router';

type InternalTourStep = {
  key: string;
  index: number;
  routeName?: string;
  title?: string;
  content?: string;
  before?: () => Promise<void>;
  after?: () => Promise<void>;
};

const state = useStateStore();
const router = useRouter();

const tourSteps = computed<InternalTourStep[]>(() =>
  steps.map((s, i) => ({ ...s, title: s.title?.(), content: s.content?.(), index: i }))
);
const step = ref<InternalTourStep>();
const show = ref(false);
const popoverShow = ref(false);
const popRef = ref<PopoverInst>();
const targetMaskRef = ref<HTMLElement>();
const activeElWatcher = ref<WatchHandle>();

function lockTargetEl(el: HTMLElement, maskEl: HTMLElement) {
  activeElWatcher.value?.stop();
  const { width, height, x, y } = useElementBounding(el, { updateTiming: 'next-frame' });
  activeElWatcher.value = watch(
    [width, height, x, y],
    () => {
      maskEl.style.opacity = '0';
      el.scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });
      maskEl.style.top = el.getBoundingClientRect().top - 8 + 'px';
      maskEl.style.left = el.getBoundingClientRect().left - 8 + 'px';
      maskEl.style.width = el.getBoundingClientRect().width + 16 + 'px';
      maskEl.style.height = el.getBoundingClientRect().height + 16 + 'px';
      maskEl.style.opacity = '1';
      popRef.value?.syncPosition();
    },
    { immediate: true }
  );
}

async function nextStep(offset: number = 1) {
  popoverShow.value = false;
  await delay(200); // give transitions some time to finish
  if (!targetMaskRef.value) return end();
  await step.value?.after?.();
  step.value = step.value ? tourSteps.value[step.value.index + offset] : tourSteps.value[0];
  if (!step.value) return end();
  if (step.value.routeName && router.currentRoute.value.name !== step.value.routeName) {
    targetMaskRef.value.style.opacity = '0';
    await router.replace({ name: step.value.routeName });
  }
  await step.value.before?.();
  const targetEl = step.value
    ? (document.querySelector(`[data-tour-key="${step.value.key}"]`) as HTMLElement) || undefined
    : undefined;
  if (!targetEl) return end();
  lockTargetEl(targetEl, targetMaskRef.value);
  popoverShow.value = true;
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
    <n-popover ref="popRef" trigger="manual" :show="popoverShow" :to="false" style="z-index: 1851">
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
    0 0 3px 2px var(--base-color),
    inset 0 0 5px 5px var(--base-color),
    0 0 0 9999px #0007;
  border-radius: 10px;
  transition: opacity 0.2s ease-in-out;
}

#tour-step-content {
  width: 512px;
  max-width: min(90vw, 768px);
  max-height: 60vh;
}
</style>
