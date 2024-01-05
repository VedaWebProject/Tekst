<script setup lang="ts">
import { NForm, NButton, type FormInst } from 'naive-ui';
import { type AnyResourceRead, type AnyUnitRead, getFullUrl, type NodeRead, GET } from '@/api';
import { ref } from 'vue';
import _cloneDeep from 'lodash.clonedeep';
import { computed, watch } from 'vue';
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
import resourceUnitFormItems from '@/forms/resources/mappings';

import EditNoteOutlined from '@vicons/material/EditNoteOutlined';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';
import ArrowBackIosOutlined from '@vicons/material/ArrowBackIosOutlined';
import ArrowForwardIosOutlined from '@vicons/material/ArrowForwardIosOutlined';
import RedoOutlined from '@vicons/material/RedoOutlined';
import FileDownloadOutlined from '@vicons/material/FileDownloadOutlined';
import FileUploadOutlined from '@vicons/material/FileUploadOutlined';

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
const node = ref<NodeRead>();
const initialModel = ref<AnyUnitRead>();
const model = ref<AnyUnitRead | undefined>(initialModel.value);
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
    node.value = (
      await GET('/nodes', {
        params: {
          query: {
            textId: state.text?.id || '',
            level: resource.value.level,
            position: newNodePosition,
            limit: 1,
          },
        },
      })
    ).data?.[0];
    if (node.value) {
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
    } else {
      gotoFirstUnit();
    }
    loadingUnit.value = false;
  },
  { immediate: true }
);

function resetForm() {
  model.value = initialModel.value;
  reset();
}

async function handleSaveClick() {
  loadingSave.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError || !model.value) return;
      // TODO ...
      loadingSave.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
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

function gotoFirstUnit() {
  router.replace({
    name: 'resourceUnits',
    params: {
      ...route.params,
      pos: 0,
    },
  });
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
          <FileDownloadOutlined />
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
          <FileUploadOutlined />
        </template>
        {{ $t('units.lblBtnUploadUnits') }}
      </n-button>
    </div>
  </div>

  <template v-if="!!resource && !!node">
    <div class="content-block">
      <h3>{{ state.textLevelLabels[node.level] }}: {{ node.label }}</h3>

      <n-form
        ref="formRef"
        :model="model"
        :rules="unitFormRules.plaintext"
        label-placement="top"
        :disabled="loading"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <component :is="resourceUnitFormItems[resource.resourceType]" v-model:model="model" />
      </n-form>

      <ButtonFooter>
        <n-button secondary :disabled="!changed" @click="resetForm">
          {{ $t('general.resetAction') }}
        </n-button>
        <n-button type="primary" :disabled="!changed" @click="handleSaveClick">
          {{ $t('general.saveAction') }}
        </n-button>
      </ButtonFooter>
    </div>
  </template>
</template>
