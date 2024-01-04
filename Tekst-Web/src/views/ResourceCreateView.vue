<script setup lang="ts">
import { POST, resourceTypes, type AnyResourceRead } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useMessages } from '@/messages';
import { computed, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { NAlert, NForm, NFormItem, NSelect, NButton, type FormInst } from 'naive-ui';
import { resourceFormRules } from '@/forms/formRules';
import { useRouter } from 'vue-router';
import ButtonFooter from '@/components/ButtonFooter.vue';
import ResourceFormItems from '@/forms/ResourceFormItems.vue';

import LayersOutlined from '@vicons/material/LayersOutlined';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';

const { message } = useMessages();
const router = useRouter();
const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();

const getInitialModel = () =>
  ({
    id: '',
    title: '',
    description: [],
    textId: state.text?.id || '',
    level: state.text?.defaultLevel || 0,
    resourceType: 'plaintext',
    ownerId: auth.user?.id || null,
    category: null,
    public: false,
    proposed: false,
    citation: null,
    meta: [],
    comment: [],
  }) as AnyResourceRead;

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const model = ref<AnyResourceRead>(getInitialModel());

const resourceTypeOptions = resourceTypes.map((lt) => ({
  label: () => $t(`resourceTypes.${lt}`),
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
    router.push({ name: 'resources', params: { text: newText?.slug } });
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
      const { data, error } = await POST('/resources', {
        body: model.value,
      });
      if (!error) {
        message.success($t('resources.create.msgSaved', { title: data.title }));
        resources.add(data);
        router.push({ name: 'resources', params: { text: state.text?.slug } });
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
  <IconHeading level="1" :icon="LayersOutlined">
    {{ $t('resources.create.heading', { text: state.text?.title }) }}
    <HelpButtonWidget help-key="resourceCreateView" />
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

  <template v-if="model">
    <n-form
      ref="formRef"
      :model="model"
      :rules="resourceFormRules"
      :disabled="loadingSave"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-alert
        type="error"
        :closable="false"
        :title="$t('general.important') + '!'"
        :show-icon="false"
        style="margin: var(--layout-gap) 0"
      >
        <p>{{ $t('resources.create.warnImmutable') }}</p>
        <!-- RESOURCE TYPE -->
        <n-form-item :label="$t('models.resource.resourceType')" path="resourceType">
          <n-select
            v-model:value="model.resourceType"
            :default-value="resourceTypeOptions[0].value"
            :placeholder="$t('models.resource.resourceType')"
            :options="resourceTypeOptions"
          />
        </n-form-item>
        <!-- STRUCTURE LEVEL -->
        <n-form-item :label="$t('models.resource.level')" path="level">
          <n-select
            v-model:value="model.level"
            :placeholder="$t('models.resource.level')"
            :options="levelOptions"
          />
        </n-form-item>
      </n-alert>
      <!-- COMMON RESOURCE FORM FIELDS -->
      <ResourceFormItems v-model:model="model" :owner="auth.user" :public="false" />
    </n-form>

    <ButtonFooter style="margin-bottom: var(--layout-gap)">
      <n-button secondary @click="handleResetClick">{{ $t('general.resetAction') }}</n-button>
      <n-button type="primary" @click="handleSaveClick">{{ $t('general.saveAction') }}</n-button>
    </ButtonFooter>
  </template>
</template>
