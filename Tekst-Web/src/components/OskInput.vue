<script setup lang="ts">
import { KeyboardIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { NButton, NDrawer, NFlex, NIcon, NInput, type InputInst } from 'naive-ui';
import type { CSSProperties } from 'vue';
import { computed, nextTick, ref } from 'vue';
import OskInputDrawerContent from './OskInputDrawerContent.vue';

const props = defineProps<{
  font?: string;
  oskKey?: string;
}>();

defineExpose({ focus: focusTargetInput, select: selectTargetInput, blur: blurTargetInput });

const model = defineModel<string | null>();

const state = useStateStore();

const showOsk = ref(false);
const targetSelectionRange = ref<[number, number]>([0, 0]);
const targetInputRef = ref<InputInst | null>(null);
const oskKey = ref<string | undefined>(props.oskKey || state.pf?.state.oskModes[0]?.key);
const oskMode = computed(() => state.pf?.state.oskModes.find((m) => m.key === oskKey.value));

const fontStyle = computed<CSSProperties>(() => ({
  fontFamily: [oskMode.value?.font, props.font, 'Tekst Content Font', 'serif']
    .filter((f) => !!f)
    .map((f) => `'${f}'`)
    .join(', '),
}));

function focusTargetInput(caretOffset?: number) {
  nextTick().then(() => {
    targetInputRef.value?.focus(); // focus element
    // for text inputs and textareas, set selection
    // (to set caret position at end of input value)
    const inputEl = targetInputRef.value?.inputElRef || targetInputRef.value?.textareaElRef;
    if (inputEl) {
      const pos = targetSelectionRange.value[0] + (caretOffset || 0);
      inputEl.setSelectionRange(pos, pos);
    }
  });
}

function selectTargetInput() {
  nextTick().then(() => {
    targetInputRef.value?.select();
  });
}

function blurTargetInput() {
  nextTick().then(() => {
    targetInputRef.value?.blur();
  });
}

function captureTargetSelectionRange() {
  const start =
    targetInputRef.value?.inputElRef?.selectionStart ??
    targetInputRef.value?.textareaElRef?.selectionStart;
  const end =
    targetInputRef.value?.inputElRef?.selectionEnd ??
    targetInputRef.value?.textareaElRef?.selectionEnd;
  targetSelectionRange.value = [
    (start ?? model.value?.length) || 0,
    (end ?? model.value?.length) || 0,
  ];
}

function handleOpen() {
  captureTargetSelectionRange();
  blurTargetInput();
  oskKey.value = props.oskKey || state.pf?.state.oskModes[0]?.key;
  showOsk.value = true;
}

function handleSubmit(value: string) {
  const oskPrefix = model.value?.substring(0, targetSelectionRange.value[0]) || '';
  const oskSuffix = model.value?.substring(targetSelectionRange.value[1]) || '';
  model.value = oskPrefix + value + oskSuffix;
  showOsk.value = false;
  focusTargetInput(value.length);
}

function handleClose() {
  showOsk.value = false;
  focusTargetInput();
}
</script>

<template>
  <n-input ref="targetInputRef" v-model:value="model" :input-props="{ style: fontStyle }">
    <template #prefix>
      <slot name="prefix"></slot>
    </template>
    <template v-if="$slots['suffix'] || !!state.pf?.state.oskModes.length" #suffix>
      <n-flex :wrap="false">
        <n-button
          v-if="!!state.pf?.state.oskModes.length"
          text
          :title="$t('osk.label')"
          :focusable="false"
          @click="handleOpen"
        >
          <template #icon>
            <n-icon :component="KeyboardIcon" />
          </template>
          <!--
          It's very ugly, but moving the OSK drawer into the button's default slot
          was the only way to make (a) the component work as a drop-in for n-input and
          (b) make the drawer show up at all
          (which doesn't work when it's inside the n-input tag).
          -->
          <n-drawer
            v-model:show="showOsk"
            placement="bottom"
            :height="800"
            style="max-height: 90%"
            @esc="handleClose"
          >
            <osk-input-drawer-content
              :initial-value="model || ''"
              :font="font"
              :osk-key="oskKey"
              @submit="handleSubmit"
              @close="handleClose"
            />
          </n-drawer>
        </n-button>
        <slot name="suffix"></slot>
      </n-flex>
    </template>
  </n-input>
</template>

<style scoped>
.key:not(.locked) {
  background-color: var(--content-bg-color);
}
</style>
