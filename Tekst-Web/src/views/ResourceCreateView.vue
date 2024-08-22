<script setup lang="ts">
import { POST, resourceTypes, type AnyResourceRead } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { computed, ref, watch, type VNodeChild, h } from 'vue';
import { RouterLink } from 'vue-router';
import {
  NIcon,
  NAlert,
  NForm,
  NFormItem,
  NSelect,
  NButton,
  type FormInst,
  type SelectOption,
} from 'naive-ui';
import { resourceSettingsFormRules } from '@/forms/formRules';
import { useRouter } from 'vue-router';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import ResourceSettingsFormItems from '@/forms/resources/config/ResourceSettingsFormItems.vue';
import { ResourceIcon, ArrowBackIcon, WarningIcon } from '@/icons';
import ResourceTypeOptionLabel from '@/components/resource/ResourceTypeOptionLabel.vue';
import { pickTranslation } from '@/utils';

const { message } = useMessages();
const router = useRouter();
const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();

const getInitialModel = () =>
  ({
    id: '',
    title: [{ locale: '*', translation: '' }],
    description: [],
    textId: state.text?.id || '',
    level: state.text?.defaultLevel || 0,
    resourceType: 'plainText',
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

const resourceTypeOptions = resourceTypes.map((rt) => ({
  label: () => $t(`resources.types.${rt}.label`),
  value: rt,
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

function renderResourceTypeOptionLabel(o: SelectOption): VNodeChild {
  return h(ResourceTypeOptionLabel, {
    label: $t(`resources.types.${o.value}.label`),
    extra: $t(`resources.types.${o.value}.parenthesis`),
  });
}

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
        message.success(
          $t('resources.create.msgSaved', { title: pickTranslation(data.title, state.locale) })
        );
        resources.add(data);
        router.push({ name: 'resources', params: { text: state.text?.slug } });
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
  <icon-heading level="1" :icon="ResourceIcon">
    {{ $t('resources.create.heading', { text: state.text?.title }) }}
    <help-button-widget help-key="resourceCreateView" />
  </icon-heading>

  <router-link
    v-slot="{ navigate }"
    :to="{ name: 'resources', params: { text: state.text?.slug } }"
    custom
  >
    <n-button text :focusable="false" @click="navigate">
      <template #icon>
        <n-icon :component="ArrowBackIcon" />
      </template>
      {{ $t('resources.backToOverview') }}
    </n-button>
  </router-link>

  <template v-if="model">
    <div class="content-block">
      <n-form
        ref="formRef"
        :model="model"
        :rules="resourceSettingsFormRules"
        :disabled="loadingSave"
        label-placement="top"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <h3>{{ $t('resources.create.headingTypeAndLevel') }}</h3>
        <n-alert type="warning" :closable="false">
          <template #icon>
            <n-icon :component="WarningIcon" />
          </template>
          <template #header>
            <div class="mb-lg">
              {{ $t('resources.create.warnImmutable') }}
            </div>
          </template>
          <!-- RESOURCE TYPE -->
          <n-form-item :label="$t('models.resource.resourceType')" path="resourceType">
            <n-select
              v-model:value="model.resourceType"
              :default-value="resourceTypeOptions[0].value"
              :placeholder="$t('models.resource.resourceType')"
              :options="resourceTypeOptions"
              :render-label="renderResourceTypeOptionLabel"
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
        <resource-settings-form-items v-model="model" :owner="auth.user" :public="false" />
      </n-form>

      <button-shelf top-gap>
        <n-button secondary @click="handleResetClick">{{ $t('general.resetAction') }}</n-button>
        <n-button type="primary" @click="handleSaveClick">{{ $t('general.saveAction') }}</n-button>
      </button-shelf>
    </div>
  </template>
</template>
