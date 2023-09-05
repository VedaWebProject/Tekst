<script setup lang="ts">
import { NButton, NIcon, NTree, useDialog, type TreeDropInfo, type TreeOption } from 'naive-ui';
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
import TagFacesOutlined from '@vicons/material/TagFacesOutlined';

const state = useStateStore();
const { message } = useMessages();
const { t } = useI18n({ useScope: 'global' });
const dialog = useDialog();

const treeData = ref<TreeOption[]>([]);
const selectedNode = ref<TreeOption | null>();

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
    { size: 'var(--app-ui-font-size-medium)', style: 'position: relative; top: 4px' },
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
    renderSuffixButton(DeleteFilled, () => handleDeleteNode(info.option)),
    renderSuffixButton(TagFacesOutlined, () => {
      alert('something');
    }),
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

  <div class="content-block">
    <n-tree
      block-line
      draggable
      :data="treeData"
      :on-load="handleLoad"
      :render-switcher-icon="renderSwitcherIcon"
      :render-label="renderLabel"
      :render-suffix="renderSuffix"
      @drop="handleDrop"
      @update:selected-keys="handleSelect"
    />
  </div>
</template>
