<script setup lang="ts">
import { useOskLayout } from '@/composables/fetchers';
import { usePlatformData } from '@/composables/platformData';
import { BackspaceIcon, CapsLockIcon, KeyboardIcon, ShiftIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { useMagicKeys, whenever } from '@vueuse/core';
import {
  NButton,
  NDrawer,
  NDrawerContent,
  NFlex,
  NIcon,
  NInput,
  NSelect,
  NSpin,
  type InputInst,
} from 'naive-ui';
import type { CSSProperties } from 'vue';
import { computed, nextTick, ref, useSlots, watch } from 'vue';
import ButtonShelf from './generic/ButtonShelf.vue';

const props = defineProps<{
  font?: string;
  preferredOsk?: string;
}>();

defineExpose({ focus: focusTargetInput, select: selectTargetInput, blur: blurTargetInput });

const model = defineModel<string | null>();

const { pfData } = usePlatformData();
const state = useStateStore();
const slots = useSlots();

const showOsk = ref(false);
const oskInput = ref<string[]>([]);
const oskInputResult = computed(() => oskInput.value.join('').normalize('NFC'));
const targetSelectionRange = ref<[number, number]>([0, 0]);

const targetInputRef = ref<InputInst | null>(null);
const oskModeSelectRef = ref<InstanceType<typeof NSelect> | null>(null);

const oskModeOptions = computed(
  () => pfData.value?.state.oskModes.map((m) => ({ label: m.name, value: m.key })) || []
);
const oskModeKey = ref<string | undefined>(props.preferredOsk);
const oskMode = computed(() =>
  pfData.value?.state.oskModes.find((m) => m.key === oskModeKey.value) || pfData.value?.state.oskModes[0]
);
const { oskLayout, loading, error } = useOskLayout(oskModeKey);

const shiftCharsPresent = computed(() =>
  oskLayout.value
    ?.flat()
    .flat()
    .some((k) => !!k.shift)
);
const shift = ref(false);
const capsLock = ref(false);
const shiftActive = computed(() => shiftCharsPresent.value && (shift.value || capsLock.value));

const fontStyle = computed<CSSProperties>(() => ({
  fontFamily: [oskMode.value?.font, props.font, 'Tekst Content Font', 'serif']
    .filter((f) => !!f)
    .map((f) => `'${f}'`)
    .join(', '),
}));

function focusTargetInput() {
  nextTick().then(() => {
    targetInputRef.value?.focus();
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
  oskModeKey.value = pfData.value?.state.oskModes[0]?.key;
  oskInput.value = [];
  shift.value = false;
  capsLock.value = false;
  showOsk.value = true;
}

function handleSubmit() {
  const preOskValue = model.value?.substring(0, targetSelectionRange.value[0]) || '';
  const postOskValue = model.value?.substring(targetSelectionRange.value[1]) || '';
  model.value = preOskValue + oskInputResult.value + postOskValue;
  const newCaretPos = targetSelectionRange.value[0] + oskInputResult.value.length;
  showOsk.value = false;
  nextTick().then(() => {
    targetInputRef.value?.focus();
    (targetInputRef.value?.inputElRef || targetInputRef.value?.textareaElRef)?.setSelectionRange(
      newCaretPos,
      newCaretPos
    );
  });
}

function handleInput(input?: string) {
  if (input) oskInput.value.push(input);
  oskModeSelectRef.value?.blur();
  shift.value = false;
}

watch(capsLock, () => (shift.value = false));

const { Enter } = useMagicKeys();

whenever(Enter, () => {
  if (showOsk.value && oskModeSelectRef.value && !oskModeSelectRef.value.focused) {
    handleSubmit();
  }
});
</script>

<template>
  <n-input
    ref="targetInputRef"
    v-bind="$attrs"
    v-model:value="model"
    :input-props="{ style: fontStyle }"
  >
    <template #prefix>
      <slot name="prefix"></slot>
    </template>
    <template v-if="slots['suffix'] || !!pfData?.state.oskModes.length" #suffix>
      <n-flex :wrap="false">
        <n-button
          v-if="!!pfData?.state.oskModes.length"
          text
          :title="$t('osk.inputBtnTip')"
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
            :height="680"
            style="max-height: 90%"
            to="#app-container"
          >
            <n-drawer-content closable>
              <template #header>
                <n-flex style="flex-wrap: wrap-reverse" align="center" class="mr-md">
                  <n-flex align="center" :wrap="false" style="flex-grow: 4; width: 200px">
                    <n-icon :component="KeyboardIcon" size="28" color="var(--accent-color)" />
                    <div
                      v-if="!!oskInput.length"
                      :style="fontStyle"
                      style="line-height: 1.5"
                      :class="{ 'text-large': !state.smallScreen, 'text-small': state.smallScreen }"
                      class="ellipsis"
                    >
                      {{ oskInputResult }}
                    </div>
                    <div v-else class="text-large translucent ellipsis">
                      {{ $t('osk.inputPlaceholder') }}
                    </div>
                    <div style="flex-grow: 2"></div>
                    <n-button
                      secondary
                      type="primary"
                      :focusable="false"
                      :disabled="!oskInput.length"
                      @click="oskInput.pop()"
                    >
                      <template #icon>
                        <n-icon :component="BackspaceIcon" />
                      </template>
                    </n-button>
                  </n-flex>
                  <n-select
                    ref="oskModeSelectRef"
                    v-model:value="oskModeKey"
                    :options="oskModeOptions"
                    style="flex-grow: 1; width: 200px"
                    :consistent-menu-width="false"
                    @update:value="() => handleInput()"
                  />
                </n-flex>
              </template>

              <n-flex align="center" justify="center" style="min-height: 100%">
                <n-flex v-if="oskLayout" vertical justify="center" align="center" :size="18">
                  <n-flex
                    v-for="(line, lineIndex) in oskLayout"
                    :key="lineIndex"
                    justify="center"
                    align="center"
                    size="large"
                  >
                    <n-flex
                      v-for="(group, groupIndex) in line"
                      :key="groupIndex"
                      justify="center"
                      align="center"
                      :size="[8, 16]"
                    >
                      <template v-for="(key, keyIndex) in group">
                        <n-button
                          v-if="!!key.char"
                          :key="keyIndex"
                          :focusable="false"
                          secondary
                          :size="state.smallScreen ? undefined : 'large'"
                          :style="fontStyle"
                          style="border: 1px solid #ddd"
                          class="box-shadow"
                          @click="handleInput(shiftActive && key.shift ? key.shift : key.char)"
                        >
                          {{ shiftActive && key.shift ? key.shift : key.char }}
                        </n-button>
                      </template>
                    </n-flex>
                  </n-flex>

                  <!-- SHIFT / CAPSLOCK -->
                  <n-flex v-if="shiftCharsPresent" justify="center" align="center" size="small">
                    <n-button
                      type="primary"
                      :size="state.smallScreen ? undefined : 'large'"
                      :secondary="!capsLock"
                      :focusable="false"
                      @click="capsLock = !capsLock"
                    >
                      <template #icon>
                        <n-icon :component="CapsLockIcon" />
                      </template>
                    </n-button>
                    <n-button
                      type="primary"
                      :size="state.smallScreen ? undefined : 'large'"
                      :secondary="!shift"
                      :focusable="false"
                      :disabled="capsLock"
                      @click="shift = !shift"
                    >
                      <template #icon>
                        <n-icon :component="ShiftIcon" />
                      </template>
                    </n-button>
                  </n-flex>
                </n-flex>

                <n-spin v-else-if="loading" class="content-loader" />

                <div v-else-if="error">
                  {{
                    $t('osk.msgErrorLoading', {
                      layout: oskMode?.name || 'unknown',
                    })
                  }}
                </div>
              </n-flex>

              <template #footer>
                <button-shelf style="width: 100%">
                  <template #start>
                    <n-button secondary :focusable="false" @click="oskInput = []">
                      {{ $t('general.resetAction') }}
                    </n-button>
                  </template>
                  <n-button secondary :focusable="false" @click="showOsk = false">
                    {{ $t('general.cancelAction') }}
                  </n-button>
                  <n-button
                    type="primary"
                    :focusable="false"
                    :disabled="loading || error"
                    @click.stop.prevent="handleSubmit"
                  >
                    {{ $t('general.insertAction') }}
                  </n-button>
                </button-shelf>
              </template>
            </n-drawer-content>
          </n-drawer>
        </n-button>
        <slot name="suffix"></slot>
      </n-flex>
    </template>
  </n-input>
</template>
