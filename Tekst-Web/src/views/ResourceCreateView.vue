<script setup lang="ts">
import { POST, resourceTypes, type AnyResourceRead } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ResourceTypeOptionLabel from '@/components/resource/ResourceTypeOptionLabel.vue';
import { useMessages } from '@/composables/messages';
import { resourceSettingsFormRules } from '@/forms/formRules';
import ResourceSettingsPropertiesFormItems from '@/forms/resources/config/ResourceSettingsPropertiesFormItems.vue';
import { $t } from '@/i18n';
import { ArrowBackIcon, ResourceIcon, WarningIcon } from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import {
  NAlert,
  NButton,
  NForm,
  NFormItem,
  NIcon,
  NSelect,
  type FormInst,
  type SelectOption,
} from 'naive-ui';
import { computed, h, ref, type VNodeChild } from 'vue';
import { onBeforeRouteUpdate, RouterLink, useRouter } from 'vue-router';

const props = defineProps<{
  textSlug?: string;
}>();

const { message } = useMessages();
const router = useRouter();
const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();

const availableResourceTypes = resourceTypes.filter(
  (rt) =>
    auth.user?.isSuperuser || (state.pf && !state.pf.state.denyResourceTypes.includes(rt.name))
);

const getInitialModel = (): AnyResourceRead =>
  ({
    title: [{ locale: '*', translation: '' }],
    textId: state.text?.id || '',
    level: state.text?.defaultLevel || 0,
    resourceType: availableResourceTypes[0].name,
    ownerId: auth.user?.id,
    public: false,
    proposed: false,
    citation: undefined,
  }) as AnyResourceRead;

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const model = ref<AnyResourceRead>(getInitialModel());

const resourceTypeOptions = availableResourceTypes.map((rt) => ({
  label: () => $t(`resources.types.${rt.name}.label`),
  value: rt.name,
}));

const levelOptions = computed(() =>
  state.textLevelLabels.map((label, i) => ({
    label: label + (state.text?.defaultLevel === i ? ` (${$t('common.default')})` : ''),
    value: i,
  }))
);

// change route if text changes
onBeforeRouteUpdate((to, from) => {
  if (to.params.textSlug !== from.params.textSlug) {
    router.push({ name: 'resources', params: { textSlug: to.params.textSlug } });
  }
});

function renderResourceTypeOptionLabel(o: SelectOption): VNodeChild {
  return h(ResourceTypeOptionLabel, {
    label: $t(`resources.types.${o.value}.label`),
    extra: $t(`resources.types.${o.value}.parenthesis`),
  });
}

function handleResetClick() {
  model.value = getInitialModel();
  formRef.value?.restoreValidation();
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
        router.push({
          name: 'resourceSettings',
          params: {
            textSlug: props.textSlug,
            id: data.id,
          },
        });
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
    :to="{ name: 'resources', params: { textSlug: props.textSlug } }"
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
              :default-value="resourceTypeOptions[0]?.value"
              :placeholder="$t('models.resource.resourceType')"
              :options="resourceTypeOptions"
              :render-label="renderResourceTypeOptionLabel"
            />
          </n-form-item>
          <!-- STRUCTURE LEVEL -->
          <n-form-item :label="$t('common.level')" path="level">
            <n-select
              v-model:value="model.level"
              :placeholder="$t('common.level')"
              :options="levelOptions"
            />
          </n-form-item>
        </n-alert>

        <!-- COMMON RESOURCE FORM FIELDS -->
        <h3>{{ $t('common.general') }}</h3>
        <resource-settings-properties-form-items v-model="model" />
      </n-form>

      <button-shelf top-gap>
        <n-button secondary @click="handleResetClick">{{ $t('common.reset') }}</n-button>
        <n-button type="primary" @click="handleSaveClick">{{ $t('common.save') }}</n-button>
      </button-shelf>
    </div>
  </template>
</template>
