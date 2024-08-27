<script setup lang="ts">
import { usePlatformData } from '@/composables/platformData';
import { CapsLockIcon, KeyboardIcon, ShiftIcon } from '@/icons';
import {
  NSpin,
  NFlex,
  NSelect,
  NInput,
  NButton,
  NIcon,
  NDrawer,
  NDrawerContent,
  type InputInst,
} from 'naive-ui';
import { computed, nextTick, ref, useSlots } from 'vue';
import ButtonShelf from './generic/ButtonShelf.vue';
import { useOskLayout } from '@/composables/fetchers';
import type { CSSProperties } from 'vue';
import { watch } from 'vue';
import { useStateStore } from '@/stores';

const props = defineProps<{
  font?: string;
}>();

defineExpose({ focus: focusTargetInput, select: selectTargetInput, blur: blurTargetInput });

const model = defineModel<string | null>();

const { pfData } = usePlatformData();
const state = useStateStore();
const slots = useSlots();

const showOsk = ref(false);
const oskInput = ref<string>('');
const targetSelectionRange = ref<[number, number]>([0, 0]);

const targetInputRef = ref<InputInst | null>(null);
const oskInputRef = ref<InputInst | null>(null);

const oskModeOptions = computed(
  () => pfData.value?.state.oskModes?.map((m) => ({ label: m.name, value: m.key })) || []
);
const oskModeKey = ref<string>();
const oskMode = computed(() =>
  pfData.value?.state.oskModes?.find((m) => m.key === oskModeKey.value)
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
  oskModeKey.value = localStorage.getItem('oskMode') || pfData.value?.state.oskModes?.[0]?.key;
  oskInput.value = '';
  shift.value = false;
  capsLock.value = false;

  nextTick().then(() => {
    oskInputRef.value?.focus();
  });

  showOsk.value = true;
}

function handleSubmit(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  const preOskValue = model.value?.substring(0, targetSelectionRange.value[0]) || '';
  const postOskValue = model.value?.substring(targetSelectionRange.value[1]) || '';
  model.value = preOskValue + oskInput.value + postOskValue;
  const newCaretPos = targetSelectionRange.value[0] + oskInput.value.length;
  showOsk.value = false;
  nextTick().then(() => {
    targetInputRef.value?.focus();
    (targetInputRef.value?.inputElRef || targetInputRef.value?.textareaElRef)?.setSelectionRange(
      newCaretPos,
      newCaretPos
    );
  });
}

function handleInput(input: string) {
  const caretPos =
    (oskInputRef.value?.inputElRef?.selectionStart ??
      oskInputRef.value?.textareaElRef?.selectionStart ??
      oskInput.value?.length) ||
    0;
  oskInput.value =
    oskInput.value?.substring(0, caretPos) + input + oskInput.value?.substring(caretPos);
  nextTick().then(() => {
    oskInputRef.value?.focus();
    oskInputRef.value?.inputElRef?.setSelectionRange(caretPos + 1, caretPos + 1);
  });
  shift.value = false;
}

function handleOskModeChange(oskModeKey: string) {
  handleInput('');
  localStorage.setItem('oskMode', oskModeKey);
}

watch(capsLock, () => (shift.value = false));
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
    <template v-if="slots['suffix'] || !!pfData?.state.oskModes?.length" #suffix>
      <n-flex :wrap="false">
        <n-button
          v-if="!!pfData?.state.oskModes?.length"
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
            :auto-focus="true"
            :height="680"
            style="max-height: 90%"
            to="#app-container"
          >
            <n-drawer-content>
              <template #header>
                <n-flex style="flex-wrap: wrap-reverse">
                  <n-input
                    ref="oskInputRef"
                    v-model:value="oskInput"
                    :placeholder="$t('osk.inputPlaceholder')"
                    style="flex-grow: 4; width: 200px"
                    :input-props="{ style: fontStyle }"
                    @keydown.enter="handleSubmit"
                  />
                  <n-select
                    v-model:value="oskModeKey"
                    :options="oskModeOptions"
                    style="flex-grow: 1; width: 200px"
                    :consistent-menu-width="false"
                    @update:value="handleOskModeChange"
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
                      size="small"
                    >
                      <template v-for="(key, keyIndex) in group">
                        <n-button
                          v-if="!!key.char"
                          :key="keyIndex"
                          :focusable="false"
                          secondary
                          :size="state.smallScreen ? undefined : 'large'"
                          :style="fontStyle"
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
                      size="large"
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
                      size="large"
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
                <button-shelf>
                  <n-button secondary :focusable="false" @click="showOsk = false">
                    {{ $t('general.cancelAction') }}
                  </n-button>
                  <n-button
                    type="primary"
                    :focusable="false"
                    :disabled="loading || error"
                    @click="handleSubmit"
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
