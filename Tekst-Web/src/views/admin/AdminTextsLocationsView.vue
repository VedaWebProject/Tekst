<script setup lang="ts">
import { DELETE, downloadData, GET, PATCH, POST, withSelectedFile } from '@/api';
import { dialogProps } from '@/common';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import EditLocationModal, {
  type EditLocationModalData,
} from '@/components/modals/EditLocationModal.vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import {
  NAlert,
  NButton,
  NFlex,
  NIcon,
  NSpin,
  NTag,
  NTree,
  useDialog,
  type TreeDragInfo,
  type TreeDropInfo,
  type TreeOption,
} from 'naive-ui';
import type { Component, Ref } from 'vue';
import { computed, h, onMounted, ref } from 'vue';

import IconHeading from '@/components/generic/IconHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { useTasks } from '@/composables/tasks';
import {
  AddIcon,
  DeleteIcon,
  DownloadIcon,
  EditIcon,
  ExpandArrowRightIcon,
  TreeIcon,
  UploadIcon,
} from '@/icons';
import { renderIcon } from '@/utils';
import { onBeforeRouteUpdate } from 'vue-router';

export interface LocationTreeOption extends TreeOption {
  level: number;
  position: number;
  parentKey: string | null | undefined;
  aliases?: string[] | null;
}

const state = useStateStore();
const { message } = useMessages();
const dialog = useDialog();
const { addTask, startTasksPolling } = useTasks();

const treeData = ref<LocationTreeOption[]>([]);
const dragNode = ref<LocationTreeOption | null>(null);
const showWarnings = ref(true);
const editModalRef = ref<InstanceType<typeof EditLocationModal> | null>(null);

const loadingAdd = ref(false);
const loadingEdit = ref(false);
const loadingDelete = ref(false);
const loadingMove = ref(false);
const loadingUpload = ref(false);
const loadingData = ref(false);
const loadingTemplate = ref(false);
const loading = computed(
  () =>
    loadingAdd.value ||
    loadingEdit.value ||
    loadingDelete.value ||
    loadingData.value ||
    loadingMove.value ||
    loadingUpload.value ||
    loadingTemplate.value
);

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
      aliases: child.aliases,
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
      parentId: (dropData.node.parentKey as string) || null,
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
    ...dialogProps,
    onPositiveClick: async () => {
      d.loading = true;
      await deleteLocation(location);
      d.loading = false;
    },
  });
}

function handleEditClick(location: LocationTreeOption) {
  editModalRef.value?.open({
    action: 'edit',
    targetId: location.key?.toString(),
    label: location.label,
    aliases: location.aliases,
  });
}

function handleAddClick(parent: LocationTreeOption | null = null) {
  editModalRef.value?.open({
    action: 'add',
    targetId: parent?.key?.toString(),
    label: undefined,
    aliases: undefined,
  });
}

async function handleAddEditSubmit(addEditData: EditLocationModalData) {
  if (addEditData.action === 'add') {
    loadingAdd.value = true;
    const parentLocation = getTreeLocationByKey(addEditData.targetId);
    const { data, error } = await POST('/locations', {
      body: {
        label: addEditData.label || '',
        level: parentLocation ? parentLocation.level + 1 : 0,
        position: Number.MAX_SAFE_INTEGER,
        textId: state.text?.id || '',
        parentId: parentLocation?.key?.toString(),
      },
    });
    if (!error) {
      message.success(
        $t('admin.text.locations.add.msgSuccess', {
          label: data.label,
          parentLabel: parentLocation?.label || state.text?.title || '',
        })
      );
    }
    await loadTreeData(parentLocation);
    loadingAdd.value = false;
  } else if (addEditData.action === 'edit') {
    loadingEdit.value = true;
    const location = getTreeLocationByKey(addEditData.targetId);
    const { data, error } = await PATCH('/locations/{id}', {
      params: { path: { id: addEditData.targetId || '' } },
      body: {
        label: addEditData.label || '',
        aliases: addEditData.aliases || undefined,
      },
    });
    if (!error) {
      message.success($t('admin.text.locations.edit.msgSuccess', { label: data.label }));
    }
    await loadTreeData(getTreeLocationByKey(location?.parentKey));
    loadingEdit.value = false;
  }
}

async function handleDownloadTemplateClick() {
  loadingTemplate.value = true;
  const { data, error } = await GET('/texts/{id}/template', {
    params: { path: { id: state.text?.id || '' } },
    parseAs: 'blob',
  });
  if (!error) {
    const filename = `${state.text?.slug}_structure_template.json`.toLowerCase();
    message.info($t('general.downloadSaved', { filename }));
    downloadData(data, filename);
  }
  loadingTemplate.value = false;
}

async function handleImportClick() {
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
      message.success($t('admin.text.locations.importSuccess'));
    }
    loadingUpload.value = false;
    loadTreeData();
  });
}

async function handleUploadClick() {
  withSelectedFile(async (file: File | null) => {
    if (!file) return;
    loadingUpload.value = true;
    const { error, data } = await PATCH('/texts/{id}/structure', {
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
      addTask(data);
      message.info($t('admin.text.locations.updateInfo'), undefined, 5);
      startTasksPolling();
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
  return h('div', { class: 'entry-label mr-lg' }, [
    h('span', { style: 'white-space: nowrap' }, `${levelLabel}: ${option.label}`),
    (option.aliases as string[])?.map((alias) => h(NTag, { size: 'small' }, () => alias)),
  ]);
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
  return h('div', { class: 'entry-suffix' }, [
    renderSuffixButton(
      EditIcon,
      () => {
        handleEditClick(info.option as LocationTreeOption);
      },
      $t('admin.text.locations.edit.heading'),
      loadingEdit
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
          () => handleAddClick(info.option as LocationTreeOption),
          $t('admin.text.locations.add.tooltip'),
          loadingAdd
        ),
  ]);
}

onBeforeRouteUpdate((to, from) => {
  if (to.params.textSlug !== from.params.textSlug) {
    loadTreeData();
  }
});

onMounted(() => {
  loadTreeData();
});
</script>

<template>
  <icon-heading level="2" :icon="TreeIcon">
    {{ $t('admin.text.locations.heading') }}
    <help-button-widget help-key="adminTextsLocationsView" />
  </icon-heading>

  <n-alert v-if="treeData.length" closable :title="$t('general.warning')" type="warning">
    {{ $t('admin.text.locations.warnGeneral') }}
  </n-alert>

  <n-alert v-if="!treeData.length && !loadingData" closable :title="$t('general.info')" type="info">
    {{ $t('admin.text.locations.infoNoLocations') }}
  </n-alert>

  <n-flex justify="space-between" size="large" class="mt-lg">
    <labeled-switch
      v-if="treeData.length"
      v-model="showWarnings"
      :label="$t('admin.text.locations.checkShowWarnings')"
    />
    <button-shelf>
      <template #start>
        <n-button
          type="primary"
          :title="$t('admin.text.locations.tipBtnAddLocationFirstLevel')"
          :disabled="loading"
          @click="handleAddClick(null)"
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
          v-if="!treeData.length"
          secondary
          :title="$t('admin.text.locations.tipBtnUploadStructure')"
          :disabled="loading"
          @click="handleImportClick()"
        >
          <template #icon>
            <n-icon :component="UploadIcon" />
          </template>
          {{ $t('admin.text.locations.lblBtnUploadStructure') }}
        </n-button>
        <n-button
          v-else
          secondary
          :title="$t('admin.text.locations.tipBtnUploadUpdates')"
          :disabled="loading"
          @click="handleUploadClick()"
        >
          <template #icon>
            <n-icon :component="UploadIcon" />
          </template>
          {{ $t('admin.text.locations.lblBtnUploadUpdates') }}
        </n-button>
      </template>
    </button-shelf>
  </n-flex>

  <div v-if="treeData.length" class="content-block" style="position: relative">
    <n-spin :show="loading" :delay="300">
      <n-tree
        id="locations-tree"
        block-line
        show-line
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
    </n-spin>
  </div>

  <n-spin v-else-if="loading" class="centered-spinner" :description="$t('general.loading')" />
  <edit-location-modal ref="editModalRef" @submit="handleAddEditSubmit" />
</template>

<style scoped>
:deep(.entry-suffix) {
  display: flex;
  gap: 4px;
  padding: 0 4px;
}

:deep(.entry-label) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  column-gap: 12px;
  row-gap: 4px;
  padding: 4px;
}
</style>
