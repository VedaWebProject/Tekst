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
  type TreeDragInfo,
} from 'naive-ui';
import { computed, h, ref } from 'vue';
import { DELETE, GET, POST } from '@/api';
import { useStateStore } from '@/stores';
import { onMounted } from 'vue';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import DeleteFilled from '@vicons/material/DeleteFilled';
import { watch } from 'vue';
import type { Component } from 'vue';

import ArrowForwardIosRound from '@vicons/material/ArrowForwardIosRound';
import EditTwotone from '@vicons/material/EditTwotone';
import { positiveButtonProps, negativeButtonProps } from '@/components/dialogButtonProps';

interface NodeTreeOption extends TreeOption {
  level: number;
  position: number;
  parentKey: string | null;
}

const state = useStateStore();
const { message } = useMessages();
const dialog = useDialog();

const treeData = ref<NodeTreeOption[]>([]);
const dragNode = ref<NodeTreeOption | null>(null);
const showWarnings = ref(true);
const deleteLoading = ref(false);
const loading = computed(() => deleteLoading.value);

async function loadTreeData(node?: TreeOption) {
  const { data, error } = await GET('/nodes/children', {
    params: {
      query: { textId: state.text?.id || '', ...(node ? { parentId: String(node.key) } : {}) },
    },
  });
  if (error) {
    message.error($t('errors.unexpected'));
    console.error(error);
    return;
  }
  const subTreeData: NodeTreeOption[] = data.map((child) => ({
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

function isDropAllowed(info: {
  dropPosition: 'before' | 'inside' | 'after';
  node: TreeOption;
  phase: 'drag' | 'drop';
}) {
  return info.dropPosition !== 'inside' && info.node.level === dragNode.value?.level;
}

function handleDragStart(data: TreeDragInfo) {
  dragNode.value = data.node as NodeTreeOption;
}

function handleDragEnd() {
  dragNode.value = null;
}

function getTreeNodeByKey(
  key: string | null,
  tree: NodeTreeOption[] = treeData.value
): NodeTreeOption | undefined {
  if (key === null) return undefined;
  const targetNode = tree.find((n) => n.key === key);
  if (targetNode) {
    return targetNode;
  } else {
    for (const node of tree) {
      if (node.children?.length) {
        const targetNode = getTreeNodeByKey(key, node.children as NodeTreeOption[]);
        if (targetNode) {
          return targetNode;
        }
      }
    }
    return undefined;
  }
}

async function handleDrop(dropData: TreeDropInfo) {
  if (dropData.dragNode.level !== dropData.node.level) {
    message.error($t('admin.texts.nodes.errorNodeLeftLevel'));
    return;
  }
  const { data, error } = await POST('/nodes/{id}/move', {
    params: {
      path: { id: dropData.dragNode.key?.toString() || '' },
    },
    body: {
      position: dropData.node.position as number,
      after: dropData.dropPosition === 'after',
      parentId: dropData.node.parentKey as string | null,
    },
  });
  if (!error) {
    message.success(
      $t('admin.texts.nodes.infoMovedNode', {
        node: data.label,
        position: data.position,
        level: state.textLevelLabels[data.level],
      })
    );
  } else {
    message.error($t('errors.unexpected'));
  }
  // update tree data
  if (dropData.dragNode.parentKey === null) {
    // no parent (level 0)
    loadTreeData();
  } else if (dropData.dragNode.parentKey === dropData.node.parentKey) {
    // same parent (load tree data for common parent)
    loadTreeData(getTreeNodeByKey(dropData.dragNode.parentKey as string | null));
  } else {
    // different parent (load tree data for both parents)
    loadTreeData(getTreeNodeByKey(dropData.dragNode.parentKey as string | null));
    loadTreeData(getTreeNodeByKey(dropData.node.parentKey as string | null));
  }
}

async function deleteNode(node: TreeOption) {
  deleteLoading.value = true;
  const { data: result, error } = await DELETE('/nodes/{id}', {
    params: { path: { id: node.key?.toString() || '' } },
  });
  if (!error) {
    loadTreeData(getTreeNodeByKey(node.parentKey as string | null));
    message.success(
      $t('admin.texts.nodes.infoDeletedNode', {
        node: node.label,
        nodes: result.nodes,
        units: result.units,
      })
    );
  } else {
    message.error($t('errors.unexpected'));
  }
  deleteLoading.value = false;
}

async function handleDeleteClick(node: TreeOption) {
  if (!showWarnings.value) {
    deleteNode(node);
    return;
  }
  dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.texts.nodes.warnDeleteNode', { nodeLabel: node.label }),
    positiveText: $t('general.deleteAction'),
    negativeText: $t('general.cancelAction'),
    positiveButtonProps: positiveButtonProps,
    negativeButtonProps: negativeButtonProps,
    autoFocus: false,
    closable: false,
    loading: deleteLoading.value,
    onPositiveClick: async () => await deleteNode(node),
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
    loading: loading.value,
    disabled: loading.value,
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
    renderSuffixButton(DeleteFilled, () => handleDeleteClick(info.option)),
  ]);
}

onMounted(() => loadTreeData());

watch(
  () => state.text?.id,
  () => {
    loadTreeData();
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
      :on-load="loadTreeData"
      :render-switcher-icon="renderSwitcherIcon"
      :render-label="renderLabel"
      :allow-drop="isDropAllowed"
      :render-suffix="renderSuffix"
      @dragstart="handleDragStart"
      @dragend="handleDragEnd"
      @drop="handleDrop"
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
