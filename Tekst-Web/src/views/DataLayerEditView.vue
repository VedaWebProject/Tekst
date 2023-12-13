<script setup lang="ts">
import { type AnyLayerUpdate, PATCH } from '@/api';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useMessages } from '@/messages';
import { computed, ref, watch } from 'vue';
import _cloneDeep from 'lodash.clonedeep';
import { RouterLink } from 'vue-router';
import { NDivider, NSpin, NForm, NButton, type FormInst } from 'naive-ui';
import { layerFormRules } from '@/forms/formRules';
import { useModelChanges } from '@/modelChanges';
import UserDisplay from '@/components/UserDisplay.vue';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';
import ButtonFooter from '@/components/ButtonFooter.vue';
import { usePlatformData } from '@/platformData';
import { useLayersStore } from '@/stores/layers';
import LayerPublicationStatus from '@/components/LayerPublicationStatus.vue';
import DataLayerForm from '@/forms/DataLayerForm.vue';

import LayersFilled from '@vicons/material/LayersFilled';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';

const { message } = useMessages();
const route = useRoute();
const router = useRouter();
const state = useStateStore();
const { pfData } = usePlatformData();

const layers = useLayersStore();
const layer = layers.data.find((l) => l.id === route.params.id);
const getInitialModel = () => _cloneDeep(layer);

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const loading = computed(() => layers.loading || loadingSave.value);
const model = ref<AnyLayerUpdate | undefined>(getInitialModel());
const { changed, reset, getChanges } = useModelChanges(model);

// change route if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'dataLayers', params: { text: newText?.slug } });
  }
);

function handleResetClick() {
  console.log(model.value);
  model.value = getInitialModel();
  reset();
}

async function handleSaveClick() {
  loadingSave.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError || !model.value) return;
      const { data, error } = await PATCH('/layers/{id}', {
        params: { path: { id: layer?.id || '' } },
        body: {
          ...(getChanges() as AnyLayerUpdate),
          layerType: model.value.layerType,
        },
      });
      if (!error) {
        message.success($t('dataLayers.edit.msgSaved', { title: data.title }));
        layers.replace(data);
      } else {
        message.error($t('errors.unexpected'), error);
      }
      loadingSave.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loadingSave.value = false;
    });
}
</script>

<template>
  <IconHeading v-if="layer" level="1" :icon="LayersFilled">
    {{ $t('dataLayers.edit.heading') }}
    <HelpButtonWidget help-key="dataLayerEditView" />
  </IconHeading>

  <router-link
    v-slot="{ navigate }"
    :to="{ name: 'dataLayers', params: { text: state.text?.slug } }"
    custom
  >
    <n-button text :focusable="false" @click="navigate">
      <template #icon>
        <KeyboardArrowLeftOutlined />
      </template>
      {{ $t('dataLayers.edit.backToOverview') }}
    </n-button>
  </router-link>

  <div v-if="model" class="content-block">
    <h2>{{ layer?.title }}</h2>

    <table v-if="layer" class="layer-info-table">
      <tbody>
        <tr>
          <td class="row-key">{{ $t('models.text.modelLabel') }}:</td>
          <td>{{ pfData?.texts?.find((t) => t.id === layer?.textId)?.title }}</td>
        </tr>
        <tr>
          <td class="row-key">{{ $t('models.text.level') }}:</td>
          <td>{{ state.textLevelLabels[layer?.level || 0] }}</td>
        </tr>
        <tr>
          <td class="row-key">{{ $t('models.user.modelLabel') }}:</td>
          <td v-if="layer?.owner"><UserDisplay :user="layer.owner" :show-icon="false" /></td>
          <td v-else>–</td>
        </tr>
        <tr>
          <td class="row-key">{{ $t('dataLayers.edit.status') }}:</td>
          <td>
            <LayerPublicationStatus :layer="layer" :show-icon="false" size="tiny" />
          </td>
        </tr>
      </tbody>
    </table>

    <n-divider />

    <n-form
      ref="formRef"
      :model="model"
      :rules="layerFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <DataLayerForm
        v-model:model="model"
        :loading="loading"
        :owner="layer?.owner"
        :public="layer?.public"
      />
    </n-form>

    <ButtonFooter>
      <n-button secondary :disabled="!changed" @click="handleResetClick">{{
        $t('general.resetAction')
      }}</n-button>
      <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
        $t('general.saveAction')
      }}</n-button>
    </ButtonFooter>
  </div>

  <n-spin v-else-if="loading" size="large" style="width: 100%" />
</template>

<style scoped>
table.layer-info-table {
  font-size: var(--app-ui-font-size-tiny);
  margin-bottom: var(--layout-gap);
}
table.layer-info-table td.row-key {
  font-weight: var(--app-ui-font-weight-normal);
  padding-right: var(--content-gap);
}
</style>
