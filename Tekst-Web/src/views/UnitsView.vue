<script setup lang="ts">
import {
  NIcon,
  NAlert,
  NDropdown,
  NSpace,
  NForm,
  NButton,
  type FormInst,
  useDialog,
} from 'naive-ui';
import {
  type AnyResourceRead,
  getFullUrl,
  type NodeRead,
  GET,
  type AnyUnitCreate,
  PATCH,
  type AnyUnitUpdate,
  POST,
  DELETE,
} from '@/api';
import { ref } from 'vue';
import { computed, watch } from 'vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import ResourceInfoWidget from '@/components/browse/widgets/ResourceInfoWidget.vue';
import { useMessages } from '@/messages';
import { useRoute, useRouter } from 'vue-router';
import { useResourcesStore } from '@/stores';
import ButtonShelf from '@/components/ButtonShelf.vue';
import { useModelChanges } from '@/modelChanges';
import { useMagicKeys, whenever } from '@vueuse/core';
import { unitFormRules } from '@/forms/formRules';
import UnitFormItems from '@/forms/resources/UnitFormItems.vue';
import { defaultUnitModels } from '@/forms/resources/defaultUnitModels';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import LocationSelectModal from '@/components/LocationSelectModal.vue';
import unitComponents from '@/components/browse/units/mappings';

import EditNoteOutlined from '@vicons/material/EditNoteOutlined';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';
import ArrowBackIosOutlined from '@vicons/material/ArrowBackIosOutlined';
import ArrowForwardIosOutlined from '@vicons/material/ArrowForwardIosOutlined';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import FileDownloadSharp from '@vicons/material/FileDownloadSharp';
import FileUploadSharp from '@vicons/material/FileUploadSharp';
import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import InsertDriveFileOutlined from '@vicons/material/InsertDriveFileOutlined';
import CompareArrowsOutlined from '@vicons/material/CompareArrowsOutlined';

type UnitFormModel = AnyUnitCreate & { id: string };

const state = useStateStore();
const resources = useResourcesStore();
const { message } = useMessages();
const router = useRouter();
const route = useRoute();
const { ArrowLeft, ArrowRight } = useMagicKeys();
const dialog = useDialog();

const showJumpToModal = ref(false);
const loading = ref(false);
const formRef = ref<FormInst | null>(null);
const resource = ref<AnyResourceRead>();
const position = computed<number>(() => Number.parseInt(route.params.pos.toString()));
const nodePath = ref<NodeRead[]>();
const node = computed<NodeRead | undefined>(() => nodePath.value?.[resource.value?.level ?? -1]);
const nodeParent = computed<NodeRead | undefined>(
  () => nodePath.value?.[(resource.value?.level ?? -1) - 1]
);
const initialUnitModel = ref<UnitFormModel>();
const model = ref<UnitFormModel | undefined>(initialUnitModel.value);
const { changed, reset, getChanges } = useModelChanges(model);

const compareResourceId = ref<string>();
const compareResource = ref<AnyResourceRead>();
const compareResourceOptions = computed(() =>
  resources.data
    .filter((r) => r.id !== resource.value?.id && r.level === resource.value?.level)
    .map((r) => ({
      label: r.title,
      key: r.id,
      disabled: r.id === compareResourceId.value,
    }))
);

// go to resource overview if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'resources', params: { text: newText?.slug } });
  }
);

async function loadNodePath() {
  if (!resource.value || !Number.isInteger(position.value)) {
    return;
  }
  loading.value = true;
  const { data, error } = await GET('/browse/nodes/path', {
    params: {
      query: {
        textId: state.text?.id || '',
        level: resource.value.level,
        position: position.value,
      },
    },
  });
  if (!error && data.length) {
    // requested node exists, set current node path
    nodePath.value = data;
    await loadUnits();
    resetForm();
  } else {
    // requested node does not exist, go back to first unit at first node
    router.replace({
      name: 'resourceUnits',
      params: {
        ...route.params,
        pos: 0,
      },
    });
  }
  loading.value = false;
}

async function loadUnits() {
  if (!nodePath.value || !resource.value) {
    return;
  }
  loading.value = true;
  const { data, error } = await GET('/units', {
    params: {
      query: {
        resourceId: [
          resource.value.id,
          ...(compareResourceId.value ? [compareResourceId.value] : []),
        ],
        nodeId: [nodePath.value[nodePath.value.length - 1].id],
        limit: 2,
      },
    },
  });
  if (!error) {
    initialUnitModel.value = data.find((u) => u.resourceId === resource.value?.id);
    const compareUnit = data.find((u) => u.resourceId === compareResourceId.value);
    if (compareUnit) {
      compareResource.value = resources.data.find((r) => r.id === compareUnit?.resourceId);
      if (compareResource.value) {
        compareResource.value.units = compareUnit ? [compareUnit] : [];
      }
    }
  } else {
    message.error($t('errors.unexpected'), error);
  }
  loading.value = false;
}

// watch for position change and resources data updates
watch(
  [position, () => resources.data],
  async ([newPosition, newResources]) => {
    if (!newResources.length || newPosition == null) {
      return;
    }
    if (!resource.value) {
      resource.value = newResources.find((l) => l.id === route.params.id.toString());
      if (!resource.value) {
        router.push({ name: 'resources', params: { text: state.text?.slug } });
        return;
      }
    }
    await loadNodePath();
  },
  { immediate: true }
);

// watch for compare resource ID change
watch(compareResourceId, async () => {
  await loadUnits();
});

function resetForm() {
  model.value = initialUnitModel.value;
  reset();
  formRef.value?.restoreValidation();
}

async function handleSaveClick() {
  loading.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError || !model.value) return;
      if (model.value.id) {
        // model has ID, so it's an update
        const { data, error } = await PATCH('/units/{id}', {
          params: { path: { id: model.value.id } },
          body: getChanges(['resourceType']) as AnyUnitUpdate,
        });
        if (!error) {
          initialUnitModel.value = data;
          resetForm();
          message.success($t('units.msgSaved'));
        } else {
          message.error($t('errors.unexpected'), error);
        }
      } else {
        // model has no ID, so it's an insert
        const { data, error } = await POST('/units', {
          body: getChanges(['resourceType']) as AnyUnitCreate,
        });
        if (!error) {
          resources.resetCoverage(resource.value?.id);
          initialUnitModel.value = data;
          resetForm();
          message.success($t('units.msgSaved'));
        } else {
          message.error($t('errors.unexpected'), error);
        }
      }
      loading.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loading.value = false;
    })
    .finally(() => {
      loading.value = false;
    });
}

async function handleJumpToClick() {
  showJumpToModal.value = true;
}

async function handleDownloadTemplateClick() {
  // As we want a proper, direct download, we let the browser handle it
  // by opening a new tab with the correct URL for the file download.
  const path = `/resources/${resource.value?.id || ''}/template`;
  window.open(getFullUrl(path), '_blank');
  message.info($t('general.downloadStarted'));
}

async function handleUploadUnitsClick() {
  // TODO: Warn for what happens and get confirmation!!!
}

async function deleteUnit() {
  if (!model.value) return;
  loading.value = true;
  const { error } = await DELETE('/units/{id}', { params: { path: { id: model.value.id } } });
  if (!error) {
    resources.resetCoverage(resource.value?.id);
    initialUnitModel.value = undefined;
    resetForm();
    message.success($t('units.msgDeleted'));
  } else {
    message.error($t('errors.unexpected'));
  }
  loading.value = false;
}

async function handleDeleteUnitClick() {
  if (!model.value) return;
  loading.value = true;
  dialog.warning({
    title: $t('general.warning'),
    content: $t('units.confirmDelete'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: deleteUnit,
    onAfterLeave: () => {
      loading.value = false;
    },
  });
}

function handleAddUnitClick() {
  if (resource.value && node.value) {
    initialUnitModel.value = {
      ...defaultUnitModels[resource.value.resourceType],
      resourceId: resource.value.id,
      resourceType: resource.value.resourceType,
      nodeId: node.value.id,
    } as UnitFormModel;
    model.value = initialUnitModel.value;
  }
}

function navigateUnits(step: number) {
  router.replace({
    name: 'resourceUnits',
    params: {
      ...route.params,
      pos: position.value + step,
    },
  });
}

function handleJumpToSubmit(nodePath: NodeRead[]) {
  router.push({
    name: 'resourceUnits',
    params: { ...route.params, pos: nodePath[nodePath.length - 1].position },
  });
}

function handleSelectcompareResource(key: string) {
  compareResourceId.value = key;
}

function handleCloseComparison() {
  compareResourceId.value = undefined;
  compareResource.value = undefined;
}

// react to keyboard for in-/decreasing location
whenever(ArrowRight, () => {
  navigateUnits(1);
});
whenever(ArrowLeft, () => {
  position.value > 0 && navigateUnits(-1);
});
</script>

<template>
  <IconHeading level="1" :icon="EditNoteOutlined">
    {{ $t('units.heading') }}
    <HelpButtonWidget help-key="unitsView" />
  </IconHeading>

  <router-link
    v-slot="{ navigate }"
    :to="{ name: 'resources', params: { text: state.text?.slug } }"
    custom
  >
    <n-button text :focusable="false" @click="navigate">
      <template #icon>
        <KeyboardArrowLeftOutlined />
      </template>
      {{ $t('resources.backToOverview') }}
    </n-button>
  </router-link>

  <h2 v-if="resource">
    {{ resource?.title }}
    <ResourceInfoWidget :resource="resource" />
  </h2>

  <ButtonShelf top-gap bottom-gap wrap-reverse>
    <template #start>
      <n-button
        type="primary"
        :disabled="loading || position === 0"
        :focusable="false"
        @click="navigateUnits(-1)"
      >
        <template #icon>
          <ArrowBackIosOutlined />
        </template>
      </n-button>
      <n-button type="primary" :disabled="loading" :focusable="false" @click="handleJumpToClick()">
        <template #icon>
          <MenuBookOutlined />
        </template>
      </n-button>
      <n-button type="primary" :disabled="loading" :focusable="false" @click="navigateUnits(1)">
        <template #icon>
          <ArrowForwardIosOutlined />
        </template>
      </n-button>
    </template>

    <n-dropdown
      trigger="click"
      :options="compareResourceOptions"
      to="#app-container"
      @select="handleSelectcompareResource"
    >
      <n-button
        secondary
        :disabled="loading || !compareResourceOptions.length"
        :focusable="false"
        :title="$t('units.lblBtnCompareTip')"
      >
        <template #icon>
          <n-icon :component="CompareArrowsOutlined" />
        </template>
        {{ $t('units.lblBtnCompare') }}
      </n-button>
    </n-dropdown>

    <n-button
      secondary
      :title="$t('units.tipBtnDownloadTemplate')"
      :disabled="loading"
      :focusable="false"
      @click="handleDownloadTemplateClick()"
    >
      <template #icon>
        <FileDownloadSharp />
      </template>
      {{ $t('units.lblBtnDownloadTemplate') }}
    </n-button>
    <n-button
      secondary
      :title="$t('units.tipBtnUploadUnits')"
      :disabled="loading"
      :focusable="false"
      @click="handleUploadUnitsClick()"
    >
      <template #icon>
        <FileUploadSharp />
      </template>
      {{ $t('units.lblBtnUploadUnits') }}
    </n-button>
  </ButtonShelf>

  <template v-if="resource && node">
    <div class="content-block">
      <IconHeading level="3" :icon="MenuBookOutlined">
        {{ state.textLevelLabels[node.level] }}: {{ node.label }}
        <template v-if="nodeParent">
          ({{ $t('general.in') }} {{ state.textLevelLabels[nodeParent.level] }}:
          {{ nodeParent.label }})
        </template>
      </IconHeading>

      <n-alert
        v-if="compareResource"
        closable
        type="default"
        style="margin-bottom: var(--layout-gap); border: 1px dashed var(--main-bg-color)"
        :title="`${compareResource.title} (${$t('units.forComparison')})`"
        :bordered="false"
        @after-leave="handleCloseComparison"
      >
        <template #icon>
          <n-icon :component="CompareArrowsOutlined" />
        </template>
        <component :is="unitComponents[compareResource.resourceType]" :resource="compareResource" />
      </n-alert>

      <template v-if="model">
        <n-form
          ref="formRef"
          :model="model"
          :rules="unitFormRules.plaintext"
          label-placement="top"
          :disabled="loading"
          label-width="auto"
          require-mark-placement="right-hanging"
        >
          <UnitFormItems v-model:model="model" />
        </n-form>

        <ButtonShelf top-gap>
          <template #start>
            <n-button secondary type="error" :disabled="loading" @click="handleDeleteUnitClick">
              {{ $t('general.deleteAction') }}
            </n-button>
          </template>
          <n-button secondary :disabled="!changed || loading" @click="resetForm">
            {{ $t('general.resetAction') }}
          </n-button>
          <n-button type="primary" :disabled="!changed || loading" @click="handleSaveClick">
            {{ $t('general.saveAction') }}
          </n-button>
        </ButtonShelf>
      </template>

      <n-space v-else vertical align="center" style="margin-bottom: var(--layout-gap)">
        <HugeLabeledIcon
          :message="$t('units.noUnit')"
          :icon="FolderOffTwotone"
          style="padding: 0 0 var(--layout-gap) 0"
        />
        <n-button type="primary" :disabled="loading" @click="handleAddUnitClick">
          <template #icon>
            <InsertDriveFileOutlined />
          </template>
          {{ $t('units.btnAddUnit') }}
        </n-button>
      </n-space>
    </div>
  </template>

  <LocationSelectModal
    v-if="resource && nodePath"
    v-model:show="showJumpToModal"
    :node-path="nodePath"
    :show-level-select="false"
    @update:node-path="handleJumpToSubmit"
  />
</template>
