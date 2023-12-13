<script setup lang="ts">
import { type AnyLayerCreate, POST, layerTypes } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore, useLayersStore, useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useMessages } from '@/messages';
import { computed, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { NAlert, NForm, NFormItem, NSelect, NButton, type FormInst } from 'naive-ui';
import { layerFormRules } from '@/forms/formRules';
import { useRouter } from 'vue-router';
import ButtonFooter from '@/components/ButtonFooter.vue';
import DataLayerForm from '@/forms/DataLayerForm.vue';

import LayersFilled from '@vicons/material/LayersFilled';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';

const { message } = useMessages();
const router = useRouter();
const state = useStateStore();
const auth = useAuthStore();
const layers = useLayersStore();

const getInitialModel = () =>
  ({
    title: '',
    description: [],
    textId: state.text?.id || '',
    level: state.text?.defaultLevel || 0,
    layerType: 'plaintext',
    ownerId: auth.user?.id || null,
    category: null,
    sharedRead: [],
    sharedWrite: [],
    public: false,
    proposed: false,
    citation: null,
    meta: [],
    comment: [],
  }) as AnyLayerCreate;

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const model = ref<AnyLayerCreate>(getInitialModel());

const layerTypeOptions = layerTypes.map((lt) => ({
  label: () => $t(`layerTypes.${lt}`),
  value: lt,
}));

const levelOptions = computed(() =>
  state.textLevelLabels.map((label, i) => ({
    label,
    value: i,
  }))
);

// change route if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'dataLayers', params: { text: newText?.slug } });
  }
);

function handleResetClick() {
  model.value = getInitialModel();
}

async function handleSaveClick() {
  loadingSave.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError || !model.value) return;
      const { data, error } = await POST('/layers', {
        body: model.value,
      });
      if (!error) {
        message.success($t('dataLayers.edit.msgSaved', { title: data.title }));
        layers.add(data);
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
  <IconHeading level="1" :icon="LayersFilled">
    {{ $t('dataLayers.create.heading', { text: state.text?.title }) }}
    <HelpButtonWidget help-key="dataLayerCreateView" />
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
    <n-form
      ref="formRef"
      :model="model"
      :rules="layerFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-alert
        type="error"
        :closable="false"
        :title="$t('general.important') + '!'"
        :show-icon="false"
        style="margin-bottom: var(--layout-gap); background-color: transparent"
      >
        <p>{{ $t('dataLayers.create.warnImmutable') }}</p>
        <!-- LAYER TYPE -->
        <n-form-item :label="$t('models.layer.layerType')" path="layerType">
          <n-select
            v-model:value="model.layerType"
            :default-value="layerTypeOptions[0].value"
            :disabled="loadingSave"
            :placeholder="$t('models.layer.layerType')"
            :options="layerTypeOptions"
          />
        </n-form-item>
        <!-- STRUCTURE LEVEL -->
        <n-form-item :label="$t('models.layer.level')" path="level">
          <n-select
            v-model:value="model.level"
            :disabled="loadingSave"
            :placeholder="$t('models.layer.level')"
            :options="levelOptions"
          />
        </n-form-item>
      </n-alert>
      <!-- COMMON DATA LAYER FORM FIELDS -->
      <DataLayerForm
        v-model:model="model"
        :loading="loadingSave"
        :owner="auth.user"
        :public="false"
      />
    </n-form>

    <ButtonFooter>
      <n-button secondary @click="handleResetClick">{{ $t('general.resetAction') }}</n-button>
      <n-button type="primary" @click="handleSaveClick">{{ $t('general.saveAction') }}</n-button>
    </ButtonFooter>
  </div>
</template>
