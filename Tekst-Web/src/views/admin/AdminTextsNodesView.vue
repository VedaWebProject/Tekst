<script setup lang="ts">
import {
  NSpin,
  NButton,
  NIcon,
  NTree,
  NAlert,
  NCheckbox,
  useDialog,
  type TreeDropInfo,
  type TreeOption,
} from 'naive-ui';
import { h, ref } from 'vue';
import { GET } from '@/api';
import { useStateStore } from '@/stores';
import { onMounted } from 'vue';
import { useMessages } from '@/messages';
import { useI18n } from 'vue-i18n';
import DeleteFilled from '@vicons/material/DeleteFilled';
import { watch } from 'vue';
import type { Component } from 'vue';

import ArrowForwardIosRound from '@vicons/material/ArrowForwardIosRound';
import EditTwotone from '@vicons/material/EditTwotone';

const state = useStateStore();
const { message } = useMessages();
const { t } = useI18n({ useScope: 'global' });
const dialog = useDialog();

const treeData = ref<TreeOption[]>([]);
const selectedNode = ref<TreeOption | null>();
const showWarnings = ref(true);

async function handleLoad(node?: TreeOption) {
  const { data, error } = await GET('/nodes/children', {
    params: {
      query: { textId: state.text?.id || '', ...(node ? { parentId: String(node.key) } : {}) },
    },
  });
  if (error) {
    message.error(t('errors.unexpected'));
    console.error(error);
    return Promise.reject(error);
  }
  const subTreeData = data.map((child) => ({
    key: child.id,
    label: child.label,
    isLeaf: child.level >= (state.text?.levels.length || Number.MAX_SAFE_INTEGER) - 1,
    level: child.level,
    position: child.position,
    parentKey: child.parentId,
  }));
  if (!node) {
    treeData.value = subTreeData;
  } else {
    node.children = subTreeData;
  }
}

function handleSelect(
  value: Array<string & number>,
  option: Array<TreeOption | null>,
  meta: {
    node: TreeOption | null;
    action: 'select' | 'unselect';
  }
) {
  selectedNode.value = meta.action === 'select' ? meta.node : null;
}

function handleDrop(data: TreeDropInfo) {
  if (data.dragNode.level !== data.node.level) {
    message.error('Text nodes can only be moved on their original structure level.');
    return;
  }
  console.log('DROP!', data);
}

function handleDeleteNode(node: TreeOption) {
  dialog.warning({
    title: t('general.warning'),
    content: t('admin.texts.nodes.warnDeleteNode', { nodeLabel: node.label }),
    positiveText: t('general.deleteAction'),
    negativeText: t('general.cancelAction'),
    style: 'font-weight: var(--app-ui-font-weight-light); width: 680px; max-width: 95%',
    onPositiveClick: async () => {
      // loading.value = true;
      //TODO
      // loading.value = false;
      console.log('DELETE!');
    },
  });
}

function renderSwitcherIcon() {
  return h(
    NIcon,
    { size: 'var(--app-ui-font-size-medium)', style: 'align-self: center' },
    {
      default: () => h(ArrowForwardIosRound),
    }
  );
}

function renderLabel({ option }: { option: TreeOption }) {
  const levelLabel = state.textLevelLabels[option.level as number];
  return h(
    'div',
    { style: 'padding: 4px' },
    {
      default: () => `${levelLabel}: ${option.label}`,
    }
  );
}

function renderSuffixButton(icon: Component, onClick: () => void) {
  return h(NButton, {
    type: 'primary',
    size: 'small',
    quaternary: true,
    circle: true,
    renderIcon: () =>
      h(NIcon, null, {
        default: () => h(icon),
      }),
    onClick: (e) => {
      e.preventDefault();
      e.stopPropagation();
      onClick();
    },
  });
}

function renderSuffix(info: { option: TreeOption; checked: boolean; selected: boolean }) {
  if (!info.selected) return null;
  return h('div', { style: 'display: flex; gap: 4px; padding: 4px' }, [
    renderSuffixButton(EditTwotone, () => {
      alert('EDIT!');
    }),
    renderSuffixButton(DeleteFilled, () => handleDeleteNode(info.option)),
  ]);
}

onMounted(() => handleLoad());

watch(
  () => state.text?.id,
  () => {
    treeData.value = [];
    handleLoad();
  }
);
</script>

<template>
  <h2>{{ $t('admin.texts.nodes.heading') }}</h2>

  <n-alert closable :title="$t('general.warning')" type="warning">
    {{ $t('admin.texts.nodes.warnGeneral') }}
  </n-alert>

  <div style="padding: var(--layout-gap) 0 0 var(--content-gap)">
    <n-checkbox v-model:checked="showWarnings">
      {{ $t('admin.texts.nodes.checkShowWarnings') }}
    </n-checkbox>
  </div>

  <div v-if="treeData.length" class="content-block">
    <n-tree
      block-line
      draggable
      :data="treeData"
      :on-load="handleLoad"
      :render-switcher-icon="renderSwitcherIcon"
      :render-label="renderLabel"
      :render-suffix="renderSuffix"
      :expand-on-dragenter="false"
      @drop="handleDrop"
      @update:selected-keys="handleSelect"
    />
  </div>

  <n-spin v-else style="margin: 3rem 0 2rem 0; width: 100%" :description="$t('init.loading')" />
</template>

<style>
.n-tree-node-switcher,
.n-tree-node-switcher--expanded {
  align-self: center;
}
</style>
