<script setup lang="ts">
import { type AnyResourceUpdate, PATCH, type AnyResourceRead } from '@/api';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useMessages } from '@/messages';
import { computed, ref, watch } from 'vue';
import _cloneDeep from 'lodash.clonedeep';
import { RouterLink } from 'vue-router';
import { NSpin, NForm, NButton, type FormInst } from 'naive-ui';
import { resourceConfigFormRules } from '@/forms/formRules';
import { useModelChanges } from '@/modelChanges';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';
import ResourceInfoWidget from '@/components/browse/widgets/ResourceInfoWidget.vue';
import ButtonFooter from '@/components/ButtonFooter.vue';
import { useResourcesStore } from '@/stores/resources';
import ResourceFormItems from '@/forms/ResourceFormItems.vue';

import SettingsFilled from '@vicons/material/SettingsFilled';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';

const { message } = useMessages();
const route = useRoute();
const router = useRouter();
const state = useStateStore();

const resources = useResourcesStore();
const resource = ref<AnyResourceRead>();
const getInitialModel = () => _cloneDeep(resource.value);

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const loading = computed(() => resources.loading || loadingSave.value);
const model = ref<AnyResourceRead | undefined>();
const { changed, reset, getChanges } = useModelChanges(model);

// change route if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'resources', params: { text: newText?.slug } });
  }
);

// watch route for resource ID and react to resource data updates
watch(
  [() => route.params.id, () => resources.data],
  ([newId, newResources]) => {
    if (!newId || !newResources.length) return;
    resource.value = newResources.find((l) => l.id === newId);
    model.value = getInitialModel();
    reset();
  },
  { immediate: true }
);

function handleResetClick() {
  model.value = getInitialModel();
  reset();
}

async function handleSaveClick() {
  loadingSave.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError || !model.value) return;
      const { data, error } = await PATCH('/resources/{id}', {
        params: { path: { id: resource.value?.id || '' } },
        body: getChanges(['resourceType']) as AnyResourceUpdate,
      });
      if (!error) {
        message.success($t('resources.settings.msgSaved', { title: data.title }));
        resources.replace(data);
        reset();
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
  <IconHeading v-if="resource" level="1" :icon="SettingsFilled">
    {{ $t('resources.settings.heading') }}
    <HelpButtonWidget help-key="ResourceConfigView" />
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

  <template v-if="model">
    <div class="content-block">
      <n-form
        ref="formRef"
        :model="model"
        :rules="resourceConfigFormRules"
        label-placement="top"
        :disabled="loading"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <ResourceFormItems
          v-model:model="model"
          :owner="resource?.owner"
          :public="resource?.public"
        />
      </n-form>

      <ButtonFooter>
        <n-button secondary :disabled="!changed" @click="handleResetClick">
          {{ $t('general.resetAction') }}
        </n-button>
        <n-button type="primary" :disabled="!changed" @click="handleSaveClick">
          {{ $t('general.saveAction') }}
        </n-button>
      </ButtonFooter>
    </div>
  </template>

  <n-spin v-else-if="loading" size="large" style="width: 100%" />
</template>

<style scoped>
table.resource-info-table {
  font-size: var(--app-ui-font-size-tiny);
  margin-bottom: var(--layout-gap);
}
table.resource-info-table td.row-key {
  font-weight: var(--app-ui-font-weight-normal);
  padding-right: var(--content-gap);
}
</style>
