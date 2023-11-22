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
import { DELETE, GET, POST, getFullUrl, type NodeRead } from '@/api';
import { useStateStore } from '@/stores';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import { watch } from 'vue';
import type { Component, Ref } from 'vue';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import RenameNodeModal from '@/components/admin/RenameNodeModal.vue';
import AddNodeModal from '@/components/admin/AddNodeModal.vue';

import AddOutlined from '@vicons/material/AddOutlined';
import DeleteFilled from '@vicons/material/DeleteFilled';
import ArrowForwardIosRound from '@vicons/material/ArrowForwardIosRound';
import EditTwotone from '@vicons/material/EditTwotone';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import FileDownloadOutlined from '@vicons/material/FileDownloadOutlined';
import FileUploadOutlined from '@vicons/material/FileUploadOutlined';
import { computed } from 'vue';

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

const loadingAdd = ref(false);
const loadingRename = ref(false);
const loadingDelete = ref(false);
const loadingMove = ref(false);
const loadingUpload = ref(false);
const loadingData = ref(false);
const loading = computed(
  () =>
    loadingAdd.value ||
    loadingRename.value ||
    loadingDelete.value ||
    loadingData.value ||
    loadingMove.value ||
    loadingUpload.value
);

const showRenameModal = ref(false);
const nodeToRename = ref<NodeTreeOption | null>(null);

const showAddModal = ref(false);
const nodeParentToAddTo = ref<NodeTreeOption | null>(null);

async function loadTreeData(node?: TreeOption) {
  loadingData.value = true;
  const { data, error } = await GET('/nodes/children', {
    params: {
      query: { textId: state.text?.id || '', ...(node ? { parentId: String(node.key) } : {}) },
    },
  });
  if (error) {
    message.error($t('errors.unexpected'), error);
    loadingData.value = false;
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
  loadingData.value = false;
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
      $t('admin.text.nodes.infoMovedNode', {
        node: data.label,
        position: data.position,
        level: state.textLevelLabels[data.level],
      })
    );
  } else {
    message.error($t('errors.unexpected'), error);
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
  loadingMove.value = true;
  if (dropData.dragNode.level !== dropData.node.level) {
    message.error($t('admin.text.nodes.errorNodeLeftLevel'));
  } else {
    await moveNode(dropData);
  }
  loadingMove.value = false;
}

async function deleteNode(node: TreeOption) {
  loadingDelete.value = true;
  const { data: result, error } = await DELETE('/nodes/{id}', {
    params: { path: { id: node.key?.toString() || '' } },
  });
  if (!error) {
    loadTreeData(getTreeNodeByKey(node.parentKey as string | null));
    message.success(
      $t('admin.text.nodes.infoDeletedNode', {
        node: node.label,
        nodes: result.nodes,
        units: result.units,
      })
    );
  } else {
    message.error($t('errors.unexpected'), error);
  }
  loadingDelete.value = false;
}

async function handleDeleteClick(node: NodeTreeOption) {
  if (!showWarnings.value) {
    deleteNode(node);
    return;
  }
  const d = dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.text.nodes.warnDeleteNode', { nodeLabel: node.label }),
    positiveText: $t('general.deleteAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: true,
    onPositiveClick: async () => {
      d.loading = true;
      await deleteNode(node);
      d.loading = false;
    },
  });
}

function handleRenameClick(node: NodeTreeOption) {
  nodeToRename.value = node;
  showRenameModal.value = true;
}

async function handleRenameResult(node: NodeRead | undefined) {
  loadingRename.value = true;
  if (node) {
    message.success(
      $t('admin.text.nodes.rename.msgSuccess', {
        oldName: nodeToRename.value?.label,
        newName: node.label,
      })
    );
  } else {
    message.error($t('errors.unexpected'));
  }
  await loadTreeData(getTreeNodeByKey(nodeToRename.value?.parentKey));
  nodeToRename.value = null;
  loadingRename.value = false;
}

function handleAddNodeClick(parent: NodeTreeOption | null = null) {
  nodeParentToAddTo.value = parent;
  showAddModal.value = true;
}

async function handleAddResult(node: NodeRead | undefined) {
  loadingAdd.value = true;
  if (node) {
    message.success(
      $t('admin.text.nodes.add.msgSuccess', {
        label: node.label,
        parentLabel: nodeParentToAddTo.value?.label || state.text?.title || '',
      })
    );
  } else {
    message.error($t('errors.unexpected'));
  }
  await loadTreeData(getTreeNodeByKey(nodeParentToAddTo.value?.key?.toString()));
  nodeParentToAddTo.value = null;
  loadingAdd.value = false;
}

async function handleDownloadTemplateClick() {
  // As we want a proper, direct download, we let the browser handle it
  // by opening a new tab with the correct URL for the file download.
  const textId = state.text?.id || '';
  const path = `/texts/${textId}/template`;
  window.open(getFullUrl(path), '_blank');
}

async function handleUploadStructureClick() {
  // unfortunately, this file upload doesn't work with our generated API client :(
  const path = `/texts/${state.text?.id || ''}/structure`;
  const endpointUrl = getFullUrl(path);
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'application/json,.json';

  input.onchange = async () => {
    if (!input.files) return;
    loadingUpload.value = true;
    const formData = new FormData();
    formData.append('file', input.files[0]);
    try {
      const response = await fetch(endpointUrl, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
        },
        body: formData,
      });
      if (response.ok) {
        message.success($t('admin.text.nodes.upload.msgSuccess'));
      } else {
        const detail = (await response.json()).detail;
        const err = new Error(detail);
        throw err;
      }
    } catch (error) {
      const err: Error = error as Error;
      message.error($t('admin.text.nodes.upload.msgError', err.message));
    } finally {
      input.remove();
      loadingUpload.value = false;
      loadTreeData();
    }
  };

  input.onclose = () => {
    input.remove();
  };

  input.click();
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

function renderSuffixButton(
  icon: Component,
  onClick: () => void,
  title?: string,
  loadingState?: Ref<boolean>
) {
  return h(NButton, {
    type: 'primary',
    size: 'small',
    quaternary: true,
    title: title,
    circle: true,
    loading: loadingState?.value ?? loading.value,
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
      $t('admin.text.nodes.rename.heading'),
      loadingRename
    ),
    renderSuffixButton(
      DeleteFilled,
      () => handleDeleteClick(info.option as NodeTreeOption),
      $t('admin.text.nodes.tipDeleteNode', { node: info.option.label || '' }),
      loadingDelete
    ),
    info.option.isLeaf
      ? null
      : renderSuffixButton(
          AddOutlined,
          () => handleAddNodeClick(info.option as NodeTreeOption),
          $t('admin.text.nodes.add.tooltip'),
          loadingAdd
        ),
  ]);
}

watch(
  () => state.text?.id,
  () => {
    loadTreeData();
  },
  { immediate: true }
);
</script>

<template>
  <h2>
    {{ $t('admin.text.nodes.heading') }}
    <HelpButtonWidget help-key="adminTextsNodesView" />
  </h2>

  <n-alert v-if="treeData.length" closable :title="$t('general.warning')" type="warning">
    {{ $t('admin.text.nodes.warnGeneral') }}
  </n-alert>

  <n-alert v-if="!treeData.length && !loadingData" closable :title="$t('general.info')" type="info">
    {{ $t('admin.text.nodes.infoNoNodes') }}
  </n-alert>

  <div
    style="
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: var(--layout-gap);
      margin-top: var(--layout-gap);
    "
  >
    <n-checkbox v-if="treeData.length" v-model:checked="showWarnings">
      {{ $t('admin.text.nodes.checkShowWarnings') }}
    </n-checkbox>
    <div style="flex-grow: 2"></div>
    <div style="display: flex; gap: 0.5rem">
      <n-button
        type="primary"
        :title="$t('admin.text.nodes.tipBtnAddNodeFirstLevel')"
        :disabled="loading"
        @click="handleAddNodeClick(null)"
      >
        <template #icon>
          <AddOutlined />
        </template>
        {{ $t('admin.text.nodes.lblBtnAddNodeFirstLevel') }}
      </n-button>
      <n-button
        secondary
        :title="$t('admin.text.nodes.tipBtnDownloadTemplate')"
        :disabled="loading"
        @click="handleDownloadTemplateClick()"
      >
        <template #icon>
          <FileDownloadOutlined />
        </template>
        {{ $t('admin.text.nodes.lblBtnDownloadTemplate') }}
      </n-button>
      <n-button
        secondary
        :title="$t('admin.text.nodes.tipBtnUploadStructure')"
        :disabled="!!treeData.length || loading"
        @click="handleUploadStructureClick()"
      >
        <template #icon>
          <FileUploadOutlined />
        </template>
        {{ $t('admin.text.nodes.lblBtnUploadStructure') }}
      </n-button>
    </div>
  </div>

  <div v-if="treeData.length" class="content-block" style="position: relative">
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
      :style="loading ? { opacity: 0.3, pointerEvents: 'none' } : {}"
      @dragstart="handleDragStart"
      @dragend="handleDragEnd"
      @drop="handleDrop"
    />
    <n-spin
      v-if="loading"
      style="position: absolute; top: 50%; left: 50%"
      :description="$t('init.loading')"
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
