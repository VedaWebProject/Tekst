<script setup lang="ts">
import { NSpace, NForm, NButton, type FormInst } from 'naive-ui';
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
import ButtonFooter from '@/components/ButtonFooter.vue';
import { useModelChanges } from '@/modelChanges';
import { useMagicKeys, whenever } from '@vueuse/core';
import { unitFormRules } from '@/forms/formRules';
import UnitFormItems from '@/forms/resources/UnitFormItems.vue';

import EditNoteOutlined from '@vicons/material/EditNoteOutlined';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';
import ArrowBackIosOutlined from '@vicons/material/ArrowBackIosOutlined';
import ArrowForwardIosOutlined from '@vicons/material/ArrowForwardIosOutlined';
import RedoOutlined from '@vicons/material/RedoOutlined';
import FileDownloadSharp from '@vicons/material/FileDownloadSharp';
import FileUploadSharp from '@vicons/material/FileUploadSharp';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import InsertDriveFileOutlined from '@vicons/material/InsertDriveFileOutlined';
import { defaultUnitModels } from '@/forms/resources/defaultUnitModels';

type UnitFormModel = AnyUnitCreate & { id: string };

const state = useStateStore();
const resources = useResourcesStore();
const { message } = useMessages();
const router = useRouter();
const route = useRoute();
const { ArrowLeft, ArrowRight } = useMagicKeys();

const loadingSave = ref(false);
const loadingUnit = ref(false);
const loading = computed(() => loadingUnit.value || loadingSave.value);

const formRef = ref<FormInst | null>(null);
const resource = ref<AnyResourceRead>();
const nodePos = computed<number>(() => Number.parseInt(route.params.pos.toString()));
const nodeParent = ref<NodeRead>();
const node = ref<NodeRead>();
const initialModel = ref<UnitFormModel>();
const model = ref<UnitFormModel | undefined>(initialModel.value);
const { changed, reset, getChanges } = useModelChanges(model);

// go to resource overview if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'resources', params: { text: newText?.slug } });
  }
);

// watch view state
watch(
  [() => resources.data, nodePos],
  async ([newResources, newNodePosition]) => {
    if (!newResources.length || newNodePosition == null) return;
    loadingUnit.value = true;
    resource.value = newResources.find((l) => l.id === route.params.id.toString());
    if (!resource.value) {
      router.push({ name: 'resources', params: { text: state.text?.slug } });
      return;
    }
    // load current node (and parents) data
    const { data, error } = await GET('/browse/nodes/path', {
      params: {
        query: {
          textId: state.text?.id || '',
          level: resource.value.level,
          position: newNodePosition,
        },
      },
    });
    if (!error && data.length) {
      // requested node exists, set current node and parent
      node.value = data.reverse()[0];
      nodeParent.value = data[1];
    } else {
      // requested node does not exist, go back to first unit at first node
      router.replace({
        name: 'resourceUnits',
        params: {
          ...route.params,
          pos: 0,
        },
      });
      return;
    }
    // load unit data
    initialModel.value = (
      await GET('/units', {
        params: {
          query: {
            resourceId: [resource.value.id],
            nodeId: [node.value.id],
            limit: 1,
          },
        },
      })
    ).data?.[0];
    resetForm();
    loadingUnit.value = false;
  },
  { immediate: true }
);

function resetForm() {
  model.value = initialModel.value;
  reset();
  formRef.value?.restoreValidation();
}

async function handleSaveClick() {
  loadingSave.value = true;
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
          initialModel.value = data;
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
          initialModel.value = data;
          resetForm();
          message.success($t('units.msgSaved'));
        } else {
          message.error($t('errors.unexpected'), error);
        }
      }
      loadingSave.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loadingSave.value = false;
    })
    .finally(() => {
      loadingSave.value = false;
    });
}

async function handleJumpToClick() {
  // TODO
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

async function handleDeleteUnitClick() {
  const { data, error } = await DELETE('');
}

function handleAddUnitClick() {
  if (resource.value && node.value) {
    initialModel.value = {
      ...defaultUnitModels[resource.value.resourceType],
      resourceId: resource.value.id,
      resourceType: resource.value.resourceType,
      nodeId: node.value.id,
    } as UnitFormModel;
    model.value = initialModel.value;
  }
}

function navigateUnits(step: number) {
  router.replace({
    name: 'resourceUnits',
    params: {
      ...route.params,
      pos: nodePos.value + step,
    },
  });
}

// react to keyboard for in-/decreasing location
whenever(ArrowRight, () => {
  navigateUnits(1);
});
whenever(ArrowLeft, () => {
  navigateUnits(-1);
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

  <div style="display: flex; gap: var(--content-gap); flex-wrap: wrap">
    <div style="display: flex; gap: var(--content-gap)">
      <n-button
        type="primary"
        :disabled="loading || nodePos === 0"
        :focusable="false"
        @click="navigateUnits(-1)"
      >
        <template #icon>
          <ArrowBackIosOutlined />
        </template>
      </n-button>
      <n-button type="primary" :disabled="loading" :focusable="false" @click="handleJumpToClick()">
        <template #icon>
          <RedoOutlined />
        </template>
      </n-button>
      <n-button type="primary" :disabled="loading" :focusable="false" @click="navigateUnits(1)">
        <template #icon>
          <ArrowForwardIosOutlined />
        </template>
      </n-button>
    </div>
    <div style="flex: 2"></div>
    <div style="display: flex; gap: var(--content-gap)">
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
    </div>
  </div>

  <template v-if="resource && node">
    <div class="content-block">
      <IconHeading level="3" :icon="MenuBookOutlined">
        {{ state.textLevelLabels[node.level] }}: {{ node.label }}
        <template v-if="nodeParent">
          ({{ $t('general.in') }} {{ state.textLevelLabels[nodeParent.level] }}:
          {{ nodeParent.label }})
        </template>
      </IconHeading>

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

        <ButtonFooter>
          <n-button secondary type="error" :disabled="loading" @click="handleDeleteUnitClick">
            {{ $t('general.deleteAction') }}
          </n-button>
          <div style="flex: 2"></div>
          <n-button secondary :disabled="!changed || loading" @click="resetForm">
            {{ $t('general.resetAction') }}
          </n-button>
          <n-button type="primary" :disabled="!changed || loading" @click="handleSaveClick">
            {{ $t('general.saveAction') }}
          </n-button>
        </ButtonFooter>
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
</template>
