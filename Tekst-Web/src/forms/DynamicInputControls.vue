<script setup lang="ts">
import { $t } from '@/i18n';
import { AddIcon, ArrowDownIcon, ArrowUpIcon, MinusIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { NButtonGroup, NButton, NIcon, type ButtonProps } from 'naive-ui';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    movable?: boolean;
    secondary?: boolean;
    topOffset?: boolean;

    moveUpTitle?: string;
    moveUpDisabled?: boolean;

    moveDownTitle?: string;
    moveDownDisabled?: boolean;

    removeTitle?: string;
    removeDisabled?: boolean;

    insertTitle?: string;
    insertDisabled?: boolean;
  }>(),
  {
    movable: true,
    moveUpTitle: $t('general.moveUpAction'),
    moveDownTitle: $t('general.moveDownAction'),
    removeTitle: $t('general.removeAction'),
    insertTitle: $t('general.insertAction'),
  }
);

defineEmits(['moveUp', 'moveDown', 'insert', 'remove']);

const state = useStateStore();

const vertical = computed(() => state.smallScreen && !props.secondary);

const btnProps = computed<ButtonProps>(() => ({
  secondary: !props.secondary,
  quaternary: props.secondary,
  type: props.secondary ? undefined : 'primary',
}));
</script>

<template>
  <div
    class="di-ctrl"
    :class="{
      'di-ctrl-primary': !secondary,
      'di-ctrl-vertical': vertical,
      'di-ctrl-top-offset': topOffset,
    }"
  >
    <n-button-group v-if="movable" :vertical="vertical">
      <n-button
        v-bind="btnProps"
        :title="moveUpTitle"
        :disabled="moveUpDisabled"
        @click="$emit('moveUp')"
      >
        <template #icon>
          <n-icon :component="ArrowUpIcon" />
        </template>
      </n-button>
      <n-button
        v-bind="btnProps"
        :title="moveDownTitle"
        :disabled="moveDownDisabled"
        @click="$emit('moveDown')"
      >
        <template #icon>
          <n-icon :component="ArrowDownIcon" />
        </template>
      </n-button>
    </n-button-group>
    <n-button-group :vertical="vertical">
      <n-button
        v-bind="btnProps"
        :title="removeTitle"
        :disabled="removeDisabled"
        @click="$emit('remove')"
      >
        <template #icon>
          <n-icon :component="MinusIcon" />
        </template>
      </n-button>
      <n-button
        v-bind="btnProps"
        :title="insertTitle"
        :disabled="insertDisabled"
        @click="$emit('insert')"
      >
        <template #icon>
          <n-icon :component="AddIcon" />
        </template>
      </n-button>
    </n-button-group>
  </div>
</template>

<style scoped>
.di-ctrl {
  position: relative;
  display: flex;
  flex-wrap: nowrap;
  align-self: stretch;
  gap: 12px;
  margin-left: var(--content-gap);
}

.di-ctrl.di-ctrl-top-offset {
  padding: 26px 0 0 0;
}

.di-ctrl.di-ctrl-primary.di-ctrl-vertical {
  justify-content: center;
}

.di-ctrl :deep(.n-button) {
  position: relative;
  padding-left: 8px;
  padding-right: 8px;
}

.di-ctrl.di-ctrl.di-ctrl-vertical :deep(.n-button) {
  left: -3px;
  padding-left: 10px;
}

.di-ctrl.di-ctrl-vertical {
  flex-direction: column;
  border-left: 3px solid var(--accent-color);
  padding: 0;
}

.di-ctrl.di-ctrl-vertical :deep(.n-button) {
  margin-left: -3px;
}
</style>
