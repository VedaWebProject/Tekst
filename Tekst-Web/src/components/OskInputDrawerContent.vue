<script setup lang="ts">
import { useOskLayout } from '@/composables/oskLayout';
import { BackspaceIcon, CapsLockIcon, KeyboardIcon, ShiftIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { useMagicKeys, whenever } from '@vueuse/core';
import { NButton, NDrawerContent, NFlex, NIcon, NSelect, NSpin } from 'naive-ui';
import type { CSSProperties } from 'vue';
import { computed, ref, watch } from 'vue';
import ButtonShelf from './generic/ButtonShelf.vue';

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
  >
    <template #header>
      <n-flex style="flex-wrap: wrap-reverse" align="center" class="mr-md">
        <n-flex align="center" :wrap="false" style="flex: 4 300px">
          <n-icon :component="KeyboardIcon" size="24" color="var(--accent-color)" />
          <div
            v-if="!!oskInput.length"
            :style="fontStyle"
            style="line-height: 1.5"
            :class="{ 'text-large': !state.smallScreen }"
            class="ellipsis"
          >
            {{ oskInputResult }}
          </div>
          <div v-else class="translucent ellipsis">
            {{ $t('osk.inputPlaceholder') }}
          </div>
          <div style="flex: 2"></div>
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
          v-model:value="oskKey"
          :options="oskModeOptions"
          style="flex: 1 200px"
          :consistent-menu-width="false"
          :disabled="oskModeOptions.length <= 1"
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
                :size="state.smallScreen ? undefined : 'large'"
                :style="fontStyle"
                class="key box-shadow"
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
            :type="capsLock ? 'primary' : undefined"
            :size="state.smallScreen ? undefined : 'large'"
            :focusable="false"
            class="key box-shadow"
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
            class="key box-shadow"
            :class="{ locked: shift }"
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
            {{ $t('common.reset') }}
          </n-button>
        </template>
        <n-button secondary :focusable="false" @click="emit('close')">
          {{ $t('common.cancel') }}
        </n-button>
        <n-button
          type="primary"
          :focusable="false"
          :disabled="loading || error"
          @click.stop.prevent="emit('submit', oskInputResult)"
        >
          {{ $t('common.insert') }}
        </n-button>
      </button-shelf>
    </template>
  </n-drawer-content>
</template>

<style scoped>
.key:not(.locked) {
  background-color: var(--content-bg-color);
}
</style>
