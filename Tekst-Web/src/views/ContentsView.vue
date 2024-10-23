<script setup lang="ts">
import {
  NIcon,
  NAlert,
  NDropdown,
  NFlex,
  NForm,
  NButton,
  NCollapseItem,
  NCollapse,
  NList,
  NBadge,
  type FormInst,
  useDialog,
} from 'naive-ui';
import {
  type AnyResourceRead,
  type LocationRead,
  GET,
  type AnyContentCreate,
  PATCH,
  type AnyContentUpdate,
  POST,
  DELETE,
} from '@/api';
import _cloneDeep from 'lodash.clonedeep';
import { ref, computed, watch } from 'vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import { useMessages } from '@/composables/messages';
import { useRoute, useRouter } from 'vue-router';
import { useResourcesStore } from '@/stores';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { useModelChanges } from '@/composables/modelChanges';
import ContentFormItems from '@/forms/resources/contents/ContentFormItems.vue';
import { defaultContentModels } from '@/forms/resources/contents/defaultContentModels';
import { dialogProps } from '@/common';
import LocationSelectModal from '@/components/modals/LocationSelectModal.vue';
import contentComponents from '@/components/content/mappings';
import LocationLabel from '@/components/LocationLabel.vue';
import CorrectionListItem from '@/components/resource/CorrectionListItem.vue';
import OtherCorrectionsListItem from '@/components/resource/OtherCorrectionsListItem.vue';
import {
  EditNoteIcon,
  ArrowBackIcon,
  ArrowForwardIcon,
  BookIcon,
  NoContentIcon,
  AddIcon,
  CompareIcon,
  VersionIcon,
  ResourceIcon,
  MoveDownIcon,
  SkipPreviousIcon,
  SkipNextIcon,
  CorrectionNoteIcon,
} from '@/icons';
import { isInputFocused, isOverlayOpen, pickTranslation, renderIcon } from '@/utils';
import { useMagicKeys, whenever } from '@vueuse/core';

type ContentFormModel = AnyContentCreate & { id: string };

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();
const { message } = useMessages();
const router = useRouter();
const route = useRoute();
const dialog = useDialog();
const { ArrowLeft, ArrowRight } = useMagicKeys();

const showJumpToModal = ref(false);
const formRef = ref<FormInst | null>(null);
const resource = ref<AnyResourceRead>();
const resourceTitle = computed(() => pickTranslation(resource.value?.title, state.locale));
const originalResourceTitle = computed(() =>
  pickTranslation(
    resources.ofText.find((r) => r.id === resource.value?.originalId)?.title,
    state.locale
  )
);
const position = computed<number>(() => Number.parseInt(route.params.pos.toString()));
const locationPath = ref<LocationRead[]>();
const location = computed<LocationRead | undefined>(
  () => locationPath.value?.[resource.value?.level ?? -1]
);
const initialContentModel = ref<ContentFormModel>();
const contentModel = ref<ContentFormModel | undefined>(initialContentModel.value);
const { changed, reset, getChanges } = useModelChanges(contentModel);

const compareResourceId = ref<string>();
const compareResource = computed<AnyResourceRead | undefined>(() =>
  resources.ofText.find((r) => r.id === compareResourceId.value)
);
const compareResourceTitle = computed(() =>
  $t('contents.forComparison', {
    title: pickTranslation(compareResource.value?.title, state.locale),
  })
);
const compareResourceOptions = computed(() =>
  resources.ofText
    .filter((r) => r.id !== resource.value?.id && r.level === resource.value?.level)
    .map((r) => ({
      label: pickTranslation(r.title, state.locale),
      key: r.id,
      disabled: r.id === compareResourceId.value,
      icon: r.originalId
        ? renderIcon(
          VersionIcon,
          r.originalId === resource.value?.id ? 'var(--accent-color)' : undefined
        )
        : renderIcon(ResourceIcon),
    }))
);

const loadingDelete = ref(false);
const loadingSave = ref(false);
const loadingData = ref(false);
const loading = computed(
  () => resources.loading || loadingDelete.value || loadingSave.value || loadingData.value
);

const corrections = computed(() => resources.corrections[resource.value?.id || ''] || []);
const prevCorrection = computed(
  () =>
    corrections.value
      .filter((c) => c.position < position.value)
      .sort((a, b) => a.position - b.position)
      .reverse()[0]
);
const nextCorrection = computed(
  () =>
    corrections.value
      .filter((c) => c.position > position.value)
      .sort((a, b) => a.position - b.position)[0]
);

const locCorrections = computed(
  () => corrections.value.filter((c) => c.position === position.value) || []
);

const otherCorrectionsCount = computed(
  () => corrections.value.length - locCorrections.value.length
);

// go to resource overview if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'resources', params: { text: newText?.slug } });
  }
);

async function loadLocationData() {
  if (!resource.value || !Number.isInteger(position.value)) {
    return;
  }
  loadingData.value = true;
  const { data: locationData, error } = await GET('/browse/location-data', {
    params: {
      query: {
        txt: state.text?.id || '',
        lvl: resource.value.level,
        pos: position.value,
        res: [
          resource.value.id,
          ...(compareResource.value?.id ? [compareResource.value.id] : []),
          ...(resource.value.originalId ? [resource.value.originalId] : []),
        ],
        head: true,
      },
    },
  });
  if (!error && locationData.locationPath?.length) {
    // requested location exists, set current location path
    locationPath.value = locationData.locationPath;
    // process received contents
    initialContentModel.value =
      locationData.contents?.find((u) => u.resourceId === resource.value?.id) ||
      (!!resource.value?.originalId &&
        locationData.contents?.find((u) => u.resourceId === resource.value?.originalId)) ||
      undefined;
    const compareContent = locationData.contents?.find(
      (u) => u.resourceId === compareResource.value?.id
    );
    if (compareResource.value) {
      compareResource.value.contents = compareContent ? [compareContent] : [];
    }
    resetForm();
  } else {
    // requested location does not exist, go back to first content at first location
    router.replace({
      name: 'resourceContents',
      params: {
        ...route.params,
        pos: 0,
      },
    });
  }
  loadingData.value = false;
}

// watch for position change and resources data updates
watch(
  [position, () => resources.ofText],
  async ([newPosition, newResources]) => {
    if (!newResources.length || newPosition == null) {
      return;
    }
    if (!resource.value) {
      resource.value = newResources.find((l) => l.id === route.params.id.toString());
      if (!resource.value) {
        router.push({ name: 'resources', params: { text: state.text?.slug } });
        return;
      }
      if (resource.value.originalId) {
        compareResourceId.value = resource.value.originalId;
      }
    }
    await loadLocationData();
  },
  { immediate: true }
);

function resetForm() {
  contentModel.value = _cloneDeep(initialContentModel.value);
  reset();
  formRef.value?.restoreValidation();
}

function handleApplyChanges() {
  const changes = compareResource.value?.contents?.[0];
  if (changes && contentModel.value) {
    contentModel.value = {
      ...contentModel.value,
      ...Object.fromEntries(
        Object.entries(changes).filter(
          (e) => !['id', 'resourceId', 'resourceType', 'locationId', 'notes'].includes(e[0])
        )
      ),
    };
  }
}

async function handleSaveClick() {
  loadingSave.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError || !contentModel.value) return;
      if (contentModel.value.id && contentModel.value.resourceId === resource.value?.id) {
        // model has ID and belongs to current resource, so it's an update
        const { data, error } = await PATCH('/contents/{id}', {
          params: { path: { id: contentModel.value.id } },
          body: getChanges(['resourceType']) as AnyContentUpdate,
        });
        if (!error) {
          initialContentModel.value = data;
          resetForm();
          message.success($t('contents.msgSaved'));
        }
      } else {
        // model has no ID or belongs to other resource (original), so it's an insert
        const { data, error } = await POST('/contents', {
          body: { ...contentModel.value, resourceId: resource.value?.id } as AnyContentCreate,
        });
        if (!error) {
          resources.resetCoverage(resource.value?.id);
          initialContentModel.value = data;
          resetForm();
          message.success($t('contents.msgSaved'));
        }
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    })
    .finally(() => {
      loadingSave.value = false;
    });
}

async function handleJumpToClick() {
  showJumpToModal.value = true;
}

async function deleteContent() {
  if (!contentModel.value) return;
  loadingDelete.value = true;
  const { error } = await DELETE('/contents/{id}', {
    params: { path: { id: contentModel.value.id } },
  });
  if (!error) {
    resources.resetCoverage(resource.value?.id);
    await loadLocationData();
    message.success($t('contents.msgDeleted'));
  }
  loadingDelete.value = false;
}

async function handleDeleteContentClick() {
  if (!contentModel.value) return;
  dialog.warning({
    title: $t('general.warning'),
    content: $t('contents.confirmDelete'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    closable: false,
    ...dialogProps,
    onPositiveClick: deleteContent,
  });
}

function handleAddContentClick() {
  if (resource.value && location.value) {
    contentModel.value = {
      ..._cloneDeep(defaultContentModels[resource.value.resourceType]),
      resourceId: resource.value.id,
      resourceType: resource.value.resourceType,
      locationId: location.value.id,
    } as ContentFormModel;
    formRef.value?.restoreValidation();
  }
}

function navigateContents(step: number) {
  router.replace({
    name: 'resourceContents',
    params: {
      ...route.params,
      pos: position.value + step,
    },
  });
}

function gotoLocation(locationPath?: LocationRead[], pos?: number) {
  if (!locationPath && pos == null) {
    console.error('Invalid location path or position', locationPath, pos);
    return;
  }
  router.push({
    name: 'resourceContents',
    params: {
      ...route.params,
      pos: locationPath ? locationPath[locationPath.length - 1].position : pos,
    },
  });
}

function handleSelectcompareResource(key: string) {
  compareResourceId.value = key;
  loadLocationData();
}

async function handleNearestChangeClick(mode: 'preceding' | 'subsequent') {
  const { data: pos, error } = await GET('/browse/nearest-content-position', {
    params: {
      query: {
        pos: position.value,
        res: compareResourceId.value || '',
        mode,
      },
    },
  });
  if (!error) {
    if (pos >= 0) {
      navigateContents(pos - position.value);
    } else {
      message.info($t('contents.msgNoNearest'));
    }
  }
}

// react to keyboard for in-/decreasing location
whenever(ArrowLeft, () => {
  if (!isOverlayOpen() && !isInputFocused()) navigateContents(-1);
});
whenever(ArrowRight, () => {
  if (!isOverlayOpen() && !isInputFocused()) navigateContents(1);
});
</script>

<template>
  <icon-heading level="1" :icon="EditNoteIcon">
    {{ $t('contents.heading') }}
    <help-button-widget help-key="contentsView" />
  </icon-heading>

  <router-link :to="{ name: 'resources', params: { text: state.text?.slug } }">
    <n-button text :focusable="false">
      <template #icon>
        <n-icon :component="ArrowBackIcon" />
      </template>
      {{ $t('resources.backToOverview') }}
    </n-button>
  </router-link>

  <icon-heading v-if="resource" level="2" :icon="resource.originalId ? VersionIcon : ResourceIcon">
    {{ resourceTitle }}
    <resource-info-widget :resource="resource" />
  </icon-heading>

  <button-shelf top-gap bottom-gap wrap="wrap-reverse">
    <template #start>
      <n-button
        type="primary"
        :disabled="loading || position === 0"
        :focusable="false"
        @click="navigateContents(-1)"
      >
        <template #icon>
          <n-icon :component="ArrowBackIcon" />
        </template>
      </n-button>
      <n-button type="primary" :disabled="loading" :focusable="false" @click="handleJumpToClick()">
        <template #icon>
          <n-icon :component="BookIcon" />
        </template>
      </n-button>
      <n-button type="primary" :disabled="loading" :focusable="false" @click="navigateContents(1)">
        <template #icon>
          <n-icon :component="ArrowForwardIcon" />
        </template>
      </n-button>
    </template>

    <n-dropdown
      trigger="click"
      :options="compareResourceOptions"
      to="#app-container"
      @select="handleSelectcompareResource"
    >
      <n-button
        secondary
        :disabled="loading || !compareResourceOptions.length"
        :focusable="false"
        :title="$t('contents.tipBtnCompare')"
      >
        <template #icon>
          <n-icon :component="CompareIcon" />
        </template>
        {{ $t('contents.lblBtnCompare') }}
      </n-button>
    </n-dropdown>
  </button-shelf>

  <template v-if="resource && locationPath">
    <div class="content-block">
      <icon-heading level="3" :icon="BookIcon">
        <location-label :location-path="locationPath" />
      </icon-heading>

      <n-alert
        v-if="
          contentModel &&
          auth.user?.isSuperuser &&
          resource.ownerId &&
          resource.ownerId !== auth.user.id
        "
        type="warning"
        closable
        :title="$t('resources.msgNotYourResourceTitle')"
        class="mb-md"
      >
        {{ $t('resources.msgNotYourResourceBody') }}
      </n-alert>

      <n-alert
        v-if="
          contentModel &&
          resource.originalId &&
          contentModel.resourceId == resource.originalId &&
          originalResourceTitle
        "
        type="info"
        closable
        :title="$t('contents.msgNoOwnContentTitle')"
        class="mb-md"
      >
        {{ $t('contents.msgNoOwnContentBody', { originalResourceTitle }) }}
      </n-alert>

      <n-alert
        v-if="compareResource"
        closable
        type="default"
        :title="compareResourceTitle"
        class="mb-lg"
        @after-leave="compareResourceId = undefined"
      >
        <template #icon>
          <n-icon :component="CompareIcon" />
        </template>
        <component
          :is="contentComponents[compareResource.resourceType]"
          v-if="compareResource.contents?.length"
          :resource="compareResource"
        />
        <span v-else style="opacity: 0.75; font-style: italic">{{ $t('contents.noContent') }}</span>

        <button-shelf
          v-if="compareResource.originalId && compareResource.originalId == resource.id"
        >
          <n-button
            secondary
            :title="$t('contents.tipBtnPrevChange')"
            @click="() => handleNearestChangeClick('preceding')"
          >
            <template #icon>
              <n-icon :component="SkipPreviousIcon" />
            </template>
          </n-button>
          <n-button
            secondary
            :title="$t('contents.tipBtnApplyChanges')"
            :disabled="!compareResource.contents?.length"
            @click="handleApplyChanges"
          >
            <template #icon>
              <n-icon :component="MoveDownIcon" />
            </template>
          </n-button>
          <n-button
            secondary
            :title="$t('contents.tipBtnNextChange')"
            @click="() => handleNearestChangeClick('subsequent')"
          >
            <template #icon>
              <n-icon :component="SkipNextIcon" />
            </template>
          </n-button>
        </button-shelf>
      </n-alert>

      <n-collapse v-if="resource && !!corrections.length" class="corrections mb-lg">
        <n-collapse-item name="corrections">
          <template #header>
            <n-badge :offset="[15, 4]">
              <template #value>
                <n-icon :component="CorrectionNoteIcon" />
              </template>
              <div>{{ $t('contents.corrections.notes') }}</div>
            </n-badge>
          </template>
          <n-list style="background-color: transparent">
            <correction-list-item
              v-for="correction in locCorrections"
              :key="correction.id"
              :resource="resource"
              :correction="correction"
              :clickable="false"
              indent
            />
            <other-corrections-list-item
              v-if="otherCorrectionsCount"
              :other-count="otherCorrectionsCount"
              :loading="loading"
              :small-screen="state.smallScreen"
              :prev-disabled="!prevCorrection"
              :next-disabled="!nextCorrection"
              indent
              @prev-click="() => gotoLocation(undefined, prevCorrection.position)"
              @next-click="() => gotoLocation(undefined, nextCorrection.position)"
            />
          </n-list>
        </n-collapse-item>
      </n-collapse>

      <template v-if="contentModel">
        <n-form
          ref="formRef"
          :model="contentModel"
          label-placement="top"
          :disabled="loading"
          label-width="auto"
          require-mark-placement="right-hanging"
        >
          <content-form-items v-model="contentModel" :resource="resource" />
        </n-form>

        <button-shelf top-gap>
          <template #start>
            <n-button
              secondary
              type="error"
              :disabled="loading || !contentModel.id || contentModel.resourceId !== resource.id"
              :loading="loadingDelete"
              @click="handleDeleteContentClick"
            >
              {{ $t('general.deleteAction') }}
            </n-button>
          </template>
          <n-button secondary :disabled="!changed || loading" @click="resetForm">
            {{ $t('general.resetAction') }}
          </n-button>
          <n-button
            v-if="!changed && resource.originalId && contentModel.resourceId == resource.originalId"
            type="primary"
            :title="$t('contents.tipBtnCopyOriginal')"
            :disabled="loading"
            @click="handleSaveClick"
          >
            {{ $t('contents.lblBtnCopyOriginal') }}
          </n-button>
          <n-button
            v-else
            type="primary"
            :disabled="loading || !changed"
            :loading="loadingSave"
            @click="handleSaveClick"
          >
            {{ $t('general.saveAction') }}
          </n-button>
        </button-shelf>
      </template>

      <n-flex v-else vertical align="center" class="mb-lg">
        <huge-labelled-icon
          :message="$t('contents.noContent')"
          :icon="NoContentIcon"
          style="padding: 0 0 var(--gap-lg) 0"
        />
        <n-button type="primary" :disabled="loading" @click="handleAddContentClick">
          <template #icon>
            <n-icon :component="AddIcon" />
          </template>
          {{ $t('contents.btnAddContent') }}
        </n-button>
      </n-flex>
    </div>
  </template>

  <location-select-modal
    v-if="resource && locationPath"
    v-model:show="showJumpToModal"
    :current-location-path="locationPath"
    :show-level-select="false"
    @submit="gotoLocation"
  />
</template>

<style scoped>
:deep(.corrections > .n-collapse-item .n-collapse-item__content-inner) {
  padding-top: 0;
}
</style>
