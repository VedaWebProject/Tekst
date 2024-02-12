<script setup lang="ts">
import {
  NSpin,
  NButton,
  NIcon,
  NTree,
  NAlert,
  useDialog,
  type TreeDropInfo,
  type TreeOption,
  type TreeDragInfo,
} from 'naive-ui';
import { h, ref } from 'vue';
import { DELETE, GET, POST, type LocationRead, withSelectedFile } from '@/api';
import { useStateStore } from '@/stores';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { watch } from 'vue';
import type { Component, Ref } from 'vue';
import { dialogProps } from '@/common';
import RenameLocationModal from '@/components/modals/RenameLocationModal.vue';
import AddLocationModal from '@/components/modals/AddLocationModal.vue';
import { computed } from 'vue';
import { saveDownload } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import {
  AddIcon,
  DeleteIcon,
  ExpandArrowRightIcon,
  EditIcon,
  DownloadIcon,
  UploadIcon,
} from '@/icons';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { renderIcon } from '@/utils';

export interface LocationTreeOption extends TreeOption {
  level: number;
  position: number;
  parentKey: string | null | undefined;
}

const state = useStateStore();
const { message } = useMessages();
const dialog = useDialog();

const treeData = ref<LocationTreeOption[]>([]);
const dragNode = ref<LocationTreeOption | null>(null);
const showWarnings = ref(true);

const loadingAdd = ref(false);
const loadingRename = ref(false);
const loadingDelete = ref(false);
const loadingMove = ref(false);
const loadingUpload = ref(false);
const loadingData = ref(false);
const loadingTemplate = ref(false);
const loading = computed(
  () =>
    loadingAdd.value ||
    loadingRename.value ||
    loadingDelete.value ||
    loadingData.value ||
    loadingMove.value ||
    loadingUpload.value ||
    loadingTemplate.value
);

const showRenameModal = ref(false);
const locationToRename = ref<LocationTreeOption | null>(null);

const showAddModal = ref(false);
const locationParentToAddTo = ref<LocationTreeOption | null>(null);

async function loadTreeData(location?: TreeOption) {
  loadingData.value = true;
  const { data, error } = await GET('/locations/children', {
    params: {
      query: { txt: state.text?.id || '', ...(location ? { parent: String(location.key) } : {}) },
    },
  });
  if (!error) {
    const subTreeData: LocationTreeOption[] = data.map((child) => ({
      key: child.id,
      label: child.label,
      isLeaf: child.level >= (state.text?.levels.length || Number.MAX_SAFE_INTEGER) - 1,
      level: child.level,
      position: child.position,
      parentKey: child.parentId,
    }));
    if (!location) {
      treeData.value = subTreeData;
    } else {
      location.children = subTreeData;
    }
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
  dragNode.value = data.node as LocationTreeOption;
}

function handleDragEnd() {
  dragNode.value = null;
}

function getTreeLocationByKey(
  key: string | null | undefined,
  tree: LocationTreeOption[] = treeData.value
): LocationTreeOption | undefined {
  if (key === null) return undefined;
  const targetLocation = tree.find((n) => n.key === key);
  if (targetLocation) {
    return targetLocation;
  } else {
    for (const location of tree) {
      if (location.children?.length) {
        const targetLocation = getTreeLocationByKey(key, location.children as LocationTreeOption[]);
        if (targetLocation) {
          return targetLocation;
        }
      }
    }
    return undefined;
  }
}

async function moveLocation(dropData: TreeDropInfo) {
  const { data, error } = await POST('/locations/{id}/move', {
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
      $t('admin.text.locations.infoMovedLocation', {
        location: data.label,
        position: data.position,
        level: state.textLevelLabels[data.level],
      })
    );
  }
  // update tree data
  if (dropData.dragNode.parentKey === null) {
    // no parent (level 0)
    await loadTreeData();
  } else if (dropData.dragNode.parentKey === dropData.node.parentKey) {
    // same parent (load tree data for common parent)
    await loadTreeData(getTreeLocationByKey(dropData.dragNode.parentKey as string | null));
  } else {
    // different parent (load tree data for both parents)
    await loadTreeData(getTreeLocationByKey(dropData.dragNode.parentKey as string | null));
    await loadTreeData(getTreeLocationByKey(dropData.node.parentKey as string | null));
  }
}

async function handleDrop(dropData: TreeDropInfo) {
  loadingMove.value = true;
  if (dropData.dragNode.level !== dropData.node.level) {
    message.error($t('admin.text.locations.errorLocationLeftLevel'));
  } else {
    await moveLocation(dropData);
  }
  loadingMove.value = false;
}

async function deleteLocation(location: TreeOption) {
  loadingDelete.value = true;
  const { data: result, error } = await DELETE('/locations/{id}', {
    params: { path: { id: location.key?.toString() || '' } },
  });
  if (!error) {
    loadTreeData(getTreeLocationByKey(location.parentKey as string | null));
    message.success(
      $t('admin.text.locations.infoDeletedLocation', {
        location: location.label,
        locations: result.locations,
        contents: result.contents,
      })
    );
  }
  loadingDelete.value = false;
}

async function handleDeleteClick(location: LocationTreeOption) {
  if (!showWarnings.value) {
    deleteLocation(location);
    return;
  }
  const d = dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.text.locations.warnDeleteLocation', { locationLabel: location.label }),
    positiveText: $t('general.deleteAction'),
    autoFocus: true,
    ...dialogProps,
    onPositiveClick: async () => {
      d.loading = true;
      await deleteLocation(location);
      d.loading = false;
    },
  });
}

function handleRenameClick(location: LocationTreeOption) {
  locationToRename.value = location;
  showRenameModal.value = true;
}

async function handleRenameResult(location: LocationRead | undefined) {
  loadingRename.value = true;
  if (location) {
    message.success(
      $t('admin.text.locations.rename.msgSuccess', {
        oldName: locationToRename.value?.label,
        newName: location.label,
      })
    );
  }
  await loadTreeData(getTreeLocationByKey(locationToRename.value?.parentKey));
  locationToRename.value = null;
  loadingRename.value = false;
}

function handleAddLocationClick(parent: LocationTreeOption | null = null) {
  locationParentToAddTo.value = parent;
  showAddModal.value = true;
}

async function handleAddResult(location: LocationRead | undefined) {
  loadingAdd.value = true;
  if (location) {
    message.success(
      $t('admin.text.locations.add.msgSuccess', {
        label: location.label,
        parentLabel: locationParentToAddTo.value?.label || state.text?.title || '',
      })
    );
  }
  await loadTreeData(getTreeLocationByKey(locationParentToAddTo.value?.key?.toString()));
  locationParentToAddTo.value = null;
  loadingAdd.value = false;
}

async function handleDownloadTemplateClick() {
  loadingTemplate.value = true;
  const { response, error } = await GET('/texts/{id}/template', {
    params: { path: { id: state.text?.id || '' } },
    parseAs: 'blob',
  });
  if (!error) {
    const filename = `${state.text?.slug}_structure_template.json`.toLowerCase();
    message.info($t('general.downloadSaved', { filename }));
    saveDownload(await response.blob(), filename);
  }
  loadingTemplate.value = false;
}

async function handleUploadStructureClick() {
  withSelectedFile(async (file: File | null) => {
    if (!file) return;
    loadingUpload.value = true;
    const { error } = await POST('/texts/{id}/structure', {
      params: { path: { id: state.text?.id || '' } },
      body: { file },
      bodySerializer(body) {
        const fd = new FormData();
        for (const [k, v] of Object.entries(body)) {
          fd.append(k, v);
        }
        return fd;
      },
    });
    if (!error) {
      message.success($t('admin.text.locations.upload.msgSuccess'));
    }
    loadingUpload.value = false;
    loadTreeData();
  });
}

function renderSwitcherIcon() {
  return h(
    NIcon,
    { size: 'var(--font-size-medium)', style: 'align-self: center' },
    {
      default: () => h(ExpandArrowRightIcon),
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
    renderIcon: renderIcon(icon),
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
      EditIcon,
      () => {
        handleRenameClick(info.option as LocationTreeOption);
      },
      $t('admin.text.locations.rename.heading'),
      loadingRename
    ),
    renderSuffixButton(
      DeleteIcon,
      () => handleDeleteClick(info.option as LocationTreeOption),
      $t('admin.text.locations.tipDeleteLocation', { location: info.option.label || '' }),
      loadingDelete
    ),
    info.option.isLeaf
      ? null
      : renderSuffixButton(
          AddIcon,
          () => handleAddLocationClick(info.option as LocationTreeOption),
          $t('admin.text.locations.add.tooltip'),
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
    {{ $t('admin.text.locations.heading') }}
    <help-button-widget help-key="adminTextsLocationsView" />
  </h2>

  <n-alert v-if="treeData.length" closable :title="$t('general.warning')" type="warning">
    {{ $t('admin.text.locations.warnGeneral') }}
  </n-alert>

  <n-alert v-if="!treeData.length && !loadingData" closable :title="$t('general.info')" type="info">
    {{ $t('admin.text.locations.infoNoLocations') }}
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
    <labelled-switch
      v-if="treeData.length"
      v-model:value="showWarnings"
      :label="$t('admin.text.locations.checkShowWarnings')"
    />
    <div style="flex-grow: 2"></div>
    <div style="display: flex; gap: 0.5rem">
      <n-button
        type="primary"
        :title="$t('admin.text.locations.tipBtnAddLocationFirstLevel')"
        :disabled="loading"
        @click="handleAddLocationClick(null)"
      >
        <template #icon>
          <n-icon :component="AddIcon" />
        </template>
        {{ $t('admin.text.locations.lblBtnAddLocationFirstLevel') }}
      </n-button>
      <n-button
        secondary
        :title="$t('admin.text.locations.tipBtnDownloadTemplate')"
        :disabled="loading"
        :loading="loadingTemplate"
        @click="handleDownloadTemplateClick()"
      >
        <template #icon>
          <n-icon :component="DownloadIcon" />
        </template>
        {{ $t('admin.text.locations.lblBtnDownloadTemplate') }}
      </n-button>
      <n-button
        secondary
        :title="$t('admin.text.locations.tipBtnUploadStructure')"
        :disabled="!!treeData.length || loading"
        @click="handleUploadStructureClick()"
      >
        <template #icon>
          <n-icon :component="UploadIcon" />
        </template>
        {{ $t('admin.text.locations.lblBtnUploadStructure') }}
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
      :description="$t('general.loading')"
    />
  </div>

  <n-spin v-else-if="loading" class="centered-spinner" :description="$t('general.loading')" />

  <rename-location-modal
    v-model:show="showRenameModal"
    :location="locationToRename"
    @submit="handleRenameResult"
  />

  <add-location-modal
    v-model:show="showAddModal"
    :parent="locationParentToAddTo"
    @submit="handleAddResult"
  />
</template>
