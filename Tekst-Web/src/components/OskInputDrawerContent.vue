<script setup lang="ts">
import { useOskLayout } from '@/composables/oskLayout';
import { BackspaceIcon, CapsLockIcon, ShiftIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { useMagicKeys, whenever } from '@vueuse/core';
import { NButton, NDivider, NDrawerContent, NFlex, NIcon, NSelect, NSpin } from 'naive-ui';
import type { CSSProperties } from 'vue';
import { computed, ref, watch } from 'vue';

const props = defineProps<{
  initialValue: string;
  font?: string;
  oskKey?: string;
}>();

const emit = defineEmits(['close', 'submit']);

const state = useStateStore();

const oskInput = ref<string[]>([]);
const oskInputResult = computed(() => oskInput.value.join('').normalize('NFC'));

const oskModeSelectRef = ref<InstanceType<typeof NSelect> | null>(null);

const oskModeOptions = computed(
  () => state.pf?.state.oskModes.map((m) => ({ label: m.name, value: m.key })) || []
);
const oskKey = ref<string | undefined>(props.oskKey || state.pf?.state.oskModes[0]?.key);
const oskMode = computed(() => state.pf?.state.oskModes.find((m) => m.key === oskKey.value));
const { oskLayout, loading, error } = useOskLayout(oskKey);

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

function handleInput(input?: string) {
  if (input) oskInput.value.push(input);
  oskModeSelectRef.value?.blur();
  shift.value = false;
}

watch(capsLock, () => (shift.value = false));

const { Enter } = useMagicKeys();

whenever(Enter, () => {
  if (oskModeSelectRef.value && !oskModeSelectRef.value.focused) {
    emit('submit', oskInputResult.value);
  }
});
</script>

<template>
  <n-drawer-content
    closable
    header-style="font-weight: normal"
    body-style="background-color: var(--main-bg-color)"
    :title="$t('osk.label')"
  >
    <n-flex vertical :size="32">
      <n-select
        ref="oskModeSelectRef"
        v-model:value="oskKey"
        :options="oskModeOptions"
        :consistent-menu-width="false"
        :disabled="oskModeOptions.length <= 1"
        @update:value="() => handleInput()"
      />
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
                :size="state.smallScreen ? undefined : 'large'"
                :style="fontStyle"
                class="key"
                @click="handleInput(shiftActive && key.shift ? key.shift : key.char)"
              >
                {{ shiftActive && key.shift ? key.shift : key.char }}
              </n-button>
            </template>
          </n-flex>
        </n-flex>

        <!-- SHIFT / CAPSLOCK / BACKSPACE -->
        <n-flex v-if="shiftCharsPresent" justify="center" align="center" size="small">
          <n-button
            :type="capsLock ? 'primary' : undefined"
            :size="state.smallScreen ? undefined : 'large'"
            :focusable="false"
            class="key"
            :class="{ locked: capsLock }"
            @click="capsLock = !capsLock"
          >
            <template #icon>
              <n-icon :component="CapsLockIcon" />
            </template>
          </n-button>
          <n-button
            :type="shift ? 'primary' : undefined"
            :size="state.smallScreen ? undefined : 'large'"
            :focusable="false"
            :disabled="capsLock"
            class="key"
            :class="{ locked: shift }"
            @click="shift = !shift"
          >
            <template #icon>
              <n-icon :component="ShiftIcon" />
            </template>
          </n-button>
          <n-button
            :size="state.smallScreen ? undefined : 'large'"
            :disabled="!oskInput.length"
            class="key"
            @click="oskInput.pop()"
          >
            <template #icon>
              <n-icon :component="BackspaceIcon" />
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
      <div style="width: 100%">
        <div
          :style="oskInputResult ? fontStyle : undefined"
          style="line-height: 1.5em"
          :class="{ 'text-large': !state.smallScreen }"
        >
          {{ oskInputResult || $t('osk.inputPlaceholder') }}
        </div>
        <n-divider />
        <n-flex justify="space-between">
          <n-button secondary :focusable="false" :disabled="!oskInputResult" @click="oskInput = []">
            {{ $t('common.reset') }}
          </n-button>
          <!-- <n-button secondary :focusable="false" @click="emit('close')">
          {{ $t('common.cancel') }}
        </n-button> -->
          <n-button
            type="primary"
            :focusable="false"
            :disabled="loading || error || !oskInputResult"
            @click.stop.prevent="emit('submit', oskInputResult)"
          >
            {{ $t('common.insert') }}
          </n-button>
        </n-flex>
      </div>
    </template>
  </n-drawer-content>
</template>

<style scoped>
.key:not(.locked) {
  background-color: var(--content-bg-color);
}
</style>
