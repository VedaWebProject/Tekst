<script setup lang="ts">
import { NButton, type FormInst } from 'naive-ui';
import { type AnyResourceRead } from '@/api';
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

import EditNoteOutlined from '@vicons/material/EditNoteOutlined';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';
import ArrowBackIosOutlined from '@vicons/material/ArrowBackIosOutlined';
import ArrowForwardIosOutlined from '@vicons/material/ArrowForwardIosOutlined';
import LocationSearchingOutlined from '@vicons/material/LocationSearchingOutlined';

const state = useStateStore();
const resources = useResourcesStore();
const { message } = useMessages();
const router = useRouter();
const route = useRoute();

const resourceId = ref<string>(route.params.id.toString());
const resource = computed<AnyResourceRead | undefined>(() =>
  resources.data.find((l) => l.id === resourceId.value)
);
const getInitialModel = () => _cloneDeep(resource.value);

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const loadingUnit = ref(false);
const loading = computed(() => loadingUnit.value || loadingSave.value);
const model = ref<AnyResourceRead | undefined>(getInitialModel());
const { changed, reset, getChanges } = useModelChanges(model);

// change route if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'resources', params: { text: newText?.slug } });
  }
);

function handleResetClick() {
  model.value = getInitialModel();
  reset();
}

async function handleSaveClick() {
  // loadingSave.value = true;
  // formRef.value
  //   ?.validate(async (validationError) => {
  //     if (validationError || !model.value) return;
  //     const { data, error } = await PATCH('/resources/{id}', {
  //       params: { path: { id: resource.value?.id || '' } },
  //       body: {
  //         ...(getChanges() as AnyResourceUpdate),
  //         resourceType: model.value.resourceType,
  //       },
  //     });
  //     if (!error) {
  //       message.success($t('resources.settings.msgSaved', { title: data.title }));
  //       resources.replace(data);
  //       reset();
  //     } else {
  //       message.error($t('errors.unexpected'), error);
  //     }
  //     loadingSave.value = false;
  //   })
  //   .catch(() => {
  //     message.error($t('errors.followFormRules'));
  //     loadingSave.value = false;
  //   });
}
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
      <n-button type="primary">
        <template #icon>
          <ArrowBackIosOutlined />
        </template>
      </n-button>
      <n-button type="primary">
        <template #icon>
          <LocationSearchingOutlined />
        </template>
      </n-button>
      <n-button type="primary">
        <template #icon>
          <ArrowForwardIosOutlined />
        </template>
      </n-button>
    </div>
    <div style="flex: 2"></div>
    <div style="display: flex; gap: var(--content-gap)">
      <n-button>foo</n-button>
      <n-button>foo</n-button>
    </div>
  </div>

  <template v-if="model">
    <div class="content-block">foo</div>

    <ButtonFooter style="margin-bottom: var(--layout-gap)">
      <n-button secondary :disabled="!changed" @click="handleResetClick">
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button type="primary" :disabled="!changed" @click="handleSaveClick">
        {{ $t('general.saveAction') }}
      </n-button>
    </ButtonFooter>
  </template>
</template>
