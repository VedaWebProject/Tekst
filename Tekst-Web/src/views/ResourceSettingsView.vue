<script setup lang="ts">
import { PATCH, type AnyResourceRead, type AnyResourceUpdate } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import { useMessages } from '@/composables/messages';
import { useModelChanges } from '@/composables/modelChanges';
import { resourceSettingsFormRules } from '@/forms/formRules';
import ResourceSettingsFormItems from '@/forms/resources/config/ResourceSettingsFormItems.vue';
import { $t } from '@/i18n';
import { ArrowBackIcon, ResourceIcon, SettingsIcon } from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { cloneDeep } from 'lodash-es';
import { NAlert, NButton, NForm, NIcon, NSpin, type FormInst } from 'naive-ui';
import { computed, ref, watch } from 'vue';
import { onBeforeRouteUpdate, RouterLink, useRouter } from 'vue-router';

const { message } = useMessages();
const router = useRouter();
const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();

const resource = ref<AnyResourceRead>();
const resourceTitle = computed(() => pickTranslation(resource.value?.title, state.locale));
const getInitialModel = () => cloneDeep(resource.value);

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const loading = computed(() => resources.loading || loadingSave.value);
const model = ref<AnyResourceRead | undefined>();
const { changed, reset, getChanges } = useModelChanges(model);

const props = defineProps<{
  textSlug?: string;
  id: string;
}>();

// change route if text changes
onBeforeRouteUpdate((to, from) => {
  if (to.params.textSlug !== from.params.textSlug) {
    router.push({ name: 'resources', params: { textSlug: to.params.textSlug } });
  }
});

// watch route for resource ID and react to resource data updates
watch(
  [() => props.id, () => resources.ofText],
  ([newId, newResources]) => {
    if (!newId || !newResources.length) return;
    resource.value = newResources.find((l) => l.id === newId);
    model.value = getInitialModel();
    reset();

    if (resource.value && !resource.value.writable) {
      message.warning($t('errors.noAccess', { resource: resourceTitle.value }));
      router.replace({ name: 'resources', params: { textSlug: props.textSlug } });
    }
  },
  { immediate: true }
);

function handleResetClick() {
  model.value = getInitialModel();
  reset();
  formRef.value?.restoreValidation();
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
        router.push({ name: 'resources', params: { textSlug: props.textSlug } });
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

  <icon-heading v-if="resource" level="2" :icon="ResourceIcon">
    {{ resourceTitle }}
    <resource-info-widget :resource="resource" />
  </icon-heading>

  <resource-info-tags v-if="resource" :resource="resource" />

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
        <resource-settings-form-items v-model="model" />
      </n-form>

      <button-shelf top-gap>
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
