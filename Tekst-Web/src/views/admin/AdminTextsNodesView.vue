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
import { h, ref } from 'vue';
import { DELETE, GET, POST, type NodeRead } from '@/api';
import { useStateStore } from '@/stores';
import { onMounted } from 'vue';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import { watch } from 'vue';
import type { Component } from 'vue';
import { positiveButtonProps, negativeButtonProps } from '@/components/dialogButtonProps';
import RenameNodeModal from '@/components/admin/RenameNodeModal.vue';
import AddNodeModal from '@/components/admin/AddNodeModal.vue';

import AddOutlined from '@vicons/material/AddOutlined';
import DeleteFilled from '@vicons/material/DeleteFilled';
import ArrowForwardIosRound from '@vicons/material/ArrowForwardIosRound';
import EditTwotone from '@vicons/material/EditTwotone';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

export interface NodeTreeOption extends TreeOption {
  level: number;
  position: number;
  parentKey: string | null | undefined;
}

const state = useStateStore();
const { message } = useMessages();
const dialog = useDialog();

const treeData = ref<NodeTreeOption[]>([]);
const dragNode = ref<NodeTreeOption | null>(null);
const showWarnings = ref(true);
const loading = ref(false);

const showRenameModal = ref(false);
const nodeToRename = ref<NodeTreeOption | null>(null);

const showAddModal = ref(false);
const nodeParentToAddTo = ref<NodeTreeOption | null>(null);

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
  key: string | null | undefined,
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

async function moveNode(dropData: TreeDropInfo) {
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
    await loadTreeData();
  } else if (dropData.dragNode.parentKey === dropData.node.parentKey) {
    // same parent (load tree data for common parent)
    await loadTreeData(getTreeNodeByKey(dropData.dragNode.parentKey as string | null));
  } else {
    // different parent (load tree data for both parents)
    await loadTreeData(getTreeNodeByKey(dropData.dragNode.parentKey as string | null));
    await loadTreeData(getTreeNodeByKey(dropData.node.parentKey as string | null));
  }
}

async function handleDrop(dropData: TreeDropInfo) {
  loading.value = true;
  if (dropData.dragNode.level !== dropData.node.level) {
    message.error($t('admin.texts.nodes.errorNodeLeftLevel'));
  } else {
    await moveNode(dropData);
  }
  loading.value = false;
}

async function deleteNode(node: TreeOption) {
  loading.value = true;
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
  loading.value = false;
}

async function handleDeleteClick(node: NodeTreeOption) {
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
    loading: loading.value,
    onPositiveClick: async () => await deleteNode(node),
  });
}

function handleRenameClick(node: NodeTreeOption) {
  nodeToRename.value = node;
  showRenameModal.value = true;
}

async function handleRenameResult(node: NodeRead | undefined) {
  loading.value = true;
  if (node) {
    message.success(
      $t('admin.texts.nodes.rename.msgSuccess', {
        oldName: nodeToRename.value?.label,
        newName: node.label,
      })
    );
  } else {
    message.error($t('errors.unexpected'));
  }
  await loadTreeData(getTreeNodeByKey(nodeToRename.value?.parentKey));
  nodeToRename.value = null;
  loading.value = false;
}

function handleAddNodeClick(parent: NodeTreeOption | null = null) {
  nodeParentToAddTo.value = parent;
  showAddModal.value = true;
}

async function handleAddResult(node: NodeRead | undefined) {
  loading.value = true;
  if (node) {
    message.success(
      $t('admin.texts.nodes.add.msgSuccess', {
        label: node.label,
        parentLabel: nodeParentToAddTo.value?.label || state.text?.title || '',
      })
    );
  } else {
    message.error($t('errors.unexpected'));
  }
  await loadTreeData(getTreeNodeByKey(nodeParentToAddTo.value?.key?.toString()));
  nodeParentToAddTo.value = null;
  loading.value = false;
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

function renderSuffixButton(icon: Component, onClick: () => void, title?: string) {
  return h(NButton, {
    type: 'primary',
    size: 'small',
    quaternary: true,
    title: title,
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
    renderSuffixButton(
      EditTwotone,
      () => {
        handleRenameClick(info.option as NodeTreeOption);
      },
      $t('admin.texts.nodes.rename.heading')
    ),
    renderSuffixButton(
      DeleteFilled,
      () => handleDeleteClick(info.option as NodeTreeOption),
      $t('admin.texts.nodes.tipDeleteNode', { node: info.option.label || '' })
    ),
    info.option.isLeaf
      ? null
      : renderSuffixButton(
          AddOutlined,
          () => handleAddNodeClick(info.option as NodeTreeOption),
          $t('admin.texts.nodes.add.tooltip')
        ),
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
  <h2>
    {{ $t('admin.texts.nodes.heading') }}
    <HelpButtonWidget />
  </h2>

  <n-alert v-if="treeData.length" closable :title="$t('general.warning')" type="warning">
    {{ $t('admin.texts.nodes.warnGeneral') }}
  </n-alert>

  <div
    style="
      display: flex;
      flex-wrap: wrap;
      justify-content: end;
      gap: var(--layout-gap);
      padding: var(--layout-gap) 0 0 var(--content-gap);
    "
  >
    <n-checkbox v-if="treeData.length" v-model:checked="showWarnings">
      {{ $t('admin.texts.nodes.checkShowWarnings') }}
    </n-checkbox>
    <div style="flex-grow: 2"></div>
    <n-button
      type="primary"
      :title="$t('admin.texts.nodes.add.btnAddNodeFirstLevelTip')"
      @click="handleAddNodeClick(null)"
    >
      <template #icon>
        <AddOutlined />
      </template>
      {{ $t('admin.texts.nodes.add.btnAddNodeFirstLevel') }}
    </n-button>
  </div>

  <div v-if="treeData.length" class="content-block">
    <n-tree
      block-line
      :draggable="!loading"
      :selectable="!loading"
      :data="treeData"
      :on-load="loadTreeData"
      :render-switcher-icon="renderSwitcherIcon"
      :render-label="renderLabel"
      :allow-drop="isDropAllowed"
      :render-suffix="renderSuffix"
      :style="loading ? { opacity: 0.5, pointerEvents: 'none' } : {}"
      @dragstart="handleDragStart"
      @dragend="handleDragEnd"
      @drop="handleDrop"
    />
  </div>

  <n-spin
    v-else-if="loading"
    style="margin: 3rem 0 2rem 0; width: 100%"
    :description="$t('init.loading')"
  />

  <RenameNodeModal
    v-model:show="showRenameModal"
    :node="nodeToRename"
    @submit="handleRenameResult"
  />

  <AddNodeModal v-model:show="showAddModal" :parent="nodeParentToAddTo" @submit="handleAddResult" />
</template>

<style>
.n-tree-node-switcher,
.n-tree-node-switcher--expanded {
  align-self: center;
}
</style>
