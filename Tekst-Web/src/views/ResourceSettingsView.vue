<script setup lang="ts">
import { type AnyResourceUpdate, PATCH, type AnyResourceRead } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { computed, ref, watch } from 'vue';
import _cloneDeep from 'lodash.clonedeep';
import { RouterLink } from 'vue-router';
import { NDivider, NIcon, NAlert, NSpin, NForm, NButton, type FormInst } from 'naive-ui';
import { resourceSettingsFormRules } from '@/forms/formRules';
import { useModelChanges } from '@/composables/modelChanges';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import ResourceSettingsFormItems from '@/forms/resources/config/ResourceSettingsFormItems.vue';

import { SettingsIcon, ArrowBackIcon, ResourceIcon } from '@/icons';
import { pickTranslation } from '@/utils';

const { message } = useMessages();
const route = useRoute();
const router = useRouter();
const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();

const resource = ref<AnyResourceRead>();
const resourceTitle = computed(() => pickTranslation(resource.value?.title, state.locale));
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
  [() => route.params.id, () => resources.ofText],
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
        message.success(
          $t('resources.settings.msgSaved', { title: pickTranslation(data.title, state.locale) })
        );
        resources.replace(data);
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
  <icon-heading v-if="resource" level="1" :icon="SettingsIcon">
    {{ $t('resources.settings.heading') }}
    <help-button-widget help-key="ResourceSettingsView" />
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

  <icon-heading v-if="resource" level="2" :icon="ResourceIcon">
    {{ resourceTitle }}
    <resource-info-widget :resource="resource" />
  </icon-heading>

  <template v-if="model">
    <div class="content-block">
      <n-alert
        v-if="
          model && auth.user?.isSuperuser && resource?.ownerId && resource.ownerId !== auth.user.id
        "
        type="warning"
        closable
        :title="$t('resources.msgNotYourResourceTitle')"
        class="mb-md"
      >
        {{ $t('resources.msgNotYourResourceBody') }}
      </n-alert>

      <n-form
        ref="formRef"
        :model="model"
        :rules="resourceSettingsFormRules"
        label-placement="top"
        :disabled="loading"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <resource-settings-form-items
          v-model="model"
          :owner="resource?.owner"
          :public="resource?.public"
        />
      </n-form>

      <n-divider />

      <button-shelf>
        <n-button secondary :disabled="!changed" @click="handleResetClick">
          {{ $t('general.resetAction') }}
        </n-button>
        <n-button type="primary" :disabled="!changed" @click="handleSaveClick">
          {{ $t('general.saveAction') }}
        </n-button>
      </button-shelf>
    </div>
  </template>

  <n-spin v-else-if="loading" class="centered-spinner" />
</template>
