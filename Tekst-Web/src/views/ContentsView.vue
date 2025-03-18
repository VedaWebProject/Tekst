<script setup lang="ts">
import {
  type AnyContentCreate,
  type AnyContentUpdate,
  type AnyResourceRead,
  type CorrectionRead,
  DELETE,
  GET,
  type LocationDataQuery,
  type LocationRead,
  PATCH,
  POST,
} from '@/api';
import { dialogProps } from '@/common';
import contentComponents from '@/components/content/mappings';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import LocationSelectModal from '@/components/modals/LocationSelectModal.vue';
import CorrectionListItem from '@/components/resource/CorrectionListItem.vue';
import OtherCorrectionsListItem from '@/components/resource/OtherCorrectionsListItem.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import { useMessages } from '@/composables/messages';
import { useModelChanges } from '@/composables/modelChanges';
import ContentFormItems from '@/forms/resources/contents/ContentFormItems.vue';
import { defaultContentModels } from '@/forms/resources/contents/defaultContentModels';
import { $t } from '@/i18n';
import {
  AddIcon,
  ArrowBackIcon,
  ArrowForwardIcon,
  BookIcon,
  CompareIcon,
  CorrectionNoteIcon,
  EditIcon,
  MoveDownIcon,
  NoContentIcon,
  ResourceIcon,
  SkipNextIcon,
  SkipPreviousIcon,
  VersionIcon,
} from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { isInputFocused, isOverlayOpen, pickTranslation, renderIcon } from '@/utils';
import { useMagicKeys, whenever } from '@vueuse/core';
import { cloneDeep } from 'lodash-es';
import {
  type FormInst,
  NAlert,
  NBadge,
  NButton,
  NCollapse,
  NCollapseItem,
  NDivider,
  NDropdown,
  NFlex,
  NForm,
  NIcon,
  NList,
  useDialog,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import { onBeforeRouteUpdate, useRouter } from 'vue-router';

type ContentFormModel = AnyContentCreate & { id: string };

const props = defineProps<{
  textSlug?: string;
  resId: string;
  locId?: string;
}>();

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();
const { message } = useMessages();
const router = useRouter();
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

const locationPath = ref<LocationRead[]>();
const location = computed<LocationRead | undefined>(
  () => locationPath.value?.[resource.value?.level ?? locationPath.value.length - 1]
);
const nextLocationId = ref<string>();
const prevLocationId = ref<string>();

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
    .sort(
      (a, b) =>
        (a.originalId === resource.value?.id ? 1 : 0) +
        (b.originalId === resource.value?.id ? 1 : 0)
    )
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
const prevCorrection = computed<CorrectionRead | undefined>(
  () =>
    corrections.value
      .filter((c) => c.position < (location.value?.position || 0))
      .sort((a, b) => a.position - b.position)
      .reverse()[0]
);
const nextCorrection = computed<CorrectionRead | undefined>(
  () =>
    corrections.value
      .filter((c) => c.position > (location.value?.position || 0))
      .sort((a, b) => a.position - b.position)[0]
);

const locCorrections = computed(
  () => corrections.value.filter((c) => c.position === location.value?.position) || []
);

const otherCorrectionsCount = computed(
  () => corrections.value.length - locCorrections.value.length
);

async function loadLocationData() {
  if (!resource.value) return;
  loadingData.value = true;
  // define part of query that will determine the target location
  const locQuery: LocationDataQuery = {
    ...(props.locId
      ? { id: props.locId }
      : // if no location ID is provided, use the current text ID and resource level
        // (will default to first location on the specified level)
        {
          txt: state.text?.id,
          lvl: resource.value.level,
        }),
  };
  // request location data
  const { data: locationData, error } = await GET('/browse', {
    params: {
      query: {
        res: [
          resource.value.id,
          ...(compareResource.value?.id ? [compareResource.value.id] : []),
          ...(resource.value.originalId ? [resource.value.originalId] : []),
        ],
        head: true,
        ...locQuery,
      },
    },
  });
  if (!error && locationData.locationPath?.length) {
    // requested location exists, set current location path, prev and next location IDs
    locationPath.value = locationData.locationPath;
    prevLocationId.value = locationData.prev || undefined;
    nextLocationId.value = locationData.next || undefined;
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
    // add location ID to URL params if not already present
    if (!props.locId) {
      router.replace({
        params: {
          locId: locationData.locationPath[locationData.locationPath.length - 1].id,
        },
      });
    }
  } else {
    // requested location does not exist, go back to first content at first location
    router.replace({
      params: {
        locId: null,
      },
    });
  }
  loadingData.value = false;
}

function resetForm() {
  contentModel.value = cloneDeep(initialContentModel.value);
  reset();
  formRef.value?.restoreValidation();
}

function copyFromComparison() {
  const changes = compareResource.value?.contents?.[0];
  if (!changes) return;
  if (!contentModel.value) handleAddContentClick();
  if (!contentModel.value) return;
  contentModel.value = {
    ...contentModel.value,
    ...Object.fromEntries(
      Object.entries(changes).filter(
        (e) => !['id', 'resourceId', 'resourceType', 'locationId', 'notes'].includes(e[0])
      )
    ),
  };
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
      ...cloneDeep(defaultContentModels[resource.value.resourceType]),
      resourceId: resource.value.id,
      resourceType: resource.value.resourceType,
      locationId: location.value.id,
    } as ContentFormModel;
    formRef.value?.restoreValidation();
  }
}

function gotoLocation(locId?: string) {
  if (!locId) {
    console.error('No location ID provided');
    return;
  }
  router.push({
    name: 'resourceContents',
    params: {
      textSlug: props.textSlug,
      resId: props.resId,
      locId,
    },
  });
}

function handleSelectcompareResource(key: string) {
  compareResourceId.value = key;
  loadLocationData();
}

async function handleNearestChangeClick(direction: 'before' | 'after') {
  const { data, error } = await GET('/browse/nearest-content-location', {
    params: {
      query: {
        loc: props.locId || '',
        res: compareResourceId.value || '',
        dir: direction,
      },
    },
  });
  if (!error) {
    gotoLocation(data.id);
  } else {
    message.info($t('contents.msgNoNearest'));
  }
}

// watch for position change and resources data updates
watch(
  [() => resources.ofText, () => props.locId],
  async ([newResources]) => {
    if (!newResources.length) {
      return;
    }
    if (!resource.value) {
      resource.value = newResources.find((l) => l.id === props.resId);
      if (!resource.value) {
        router.replace({ name: 'resources', params: { textSlug: state.text?.slug } });
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

// go to resource overview if text changes
onBeforeRouteUpdate((to, from) => {
  if (to.params.textSlug !== from.params.textSlug) {
    router.push({ name: 'resources', params: { textSlug: to.params.textSlug } });
  }
});

// react to keyboard for in-/decreasing location
whenever(ArrowLeft, () => {
  if (!isOverlayOpen() && !isInputFocused()) gotoLocation(prevLocationId.value);
});
whenever(ArrowRight, () => {
  if (!isOverlayOpen() && !isInputFocused()) gotoLocation(nextLocationId.value);
});
</script>

<template>
  <icon-heading level="1" :icon="EditIcon">
    {{ $t('contents.heading') }}
    <help-button-widget help-key="contentsView" />
  </icon-heading>

  <router-link :to="{ name: 'resources', params: { textSlug: state.text?.slug } }">
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
    <resource-info-tags
       v-if="!state.smallScreen"
      :resource="resource"
      reverse
      style="flex: 2; justify-content: end"
    />
  </icon-heading>

  <button-shelf top-gap bottom-gap wrap="wrap-reverse" class="gray-box">
    <template #start>
      <n-button
        type="primary"
        :disabled="loading || !prevLocationId"
        :focusable="false"
        @click="gotoLocation(prevLocationId)"
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
      <n-button
        type="primary"
        :disabled="loading || !nextLocationId"
        :focusable="false"
        @click="gotoLocation(nextLocationId)"
      >
        <template #icon>
          <n-icon :component="ArrowForwardIcon" />
        </template>
      </n-button>
    </template>

    <n-dropdown
      trigger="click"
      :options="compareResourceOptions"
      placement="bottom-end"
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

      <!-- ALERT: THIS IS NOT YOUR RESOURCE! -->
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

      <!-- ALERT: NO OWN CONTENT AT THIS LOCATION! -->
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

      <!-- COMPARISON WITH OTHER RESOURCE -->
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
        <template v-if="compareResource.contents?.length">
          <component
            :is="contentComponents[compareResource.resourceType]"
            :resource="compareResource"
            :dir="resource.config.common.rtl ? 'rtl' : undefined"
            class="mt-md"
          />
          <div v-if="compareResource.contents[0]?.comment" class="text-small translucent">
            <n-divider />
            <strong>{{ $t('resources.types.common.contentFields.comment') }}:</strong>
            {{ compareResource.contents[0].comment }}
          </div>
        </template>
        <span v-else style="opacity: 0.75; font-style: italic">{{ $t('contents.noContent') }}</span>

        <button-shelf v-if="compareResource.resourceType == resource.resourceType">
          <n-button
            secondary
            :title="$t('contents.tipBtnPrevChange')"
            @click="() => handleNearestChangeClick('before')"
          >
            <template #icon>
              <n-icon :component="SkipPreviousIcon" />
            </template>
          </n-button>
          <n-button
            secondary
            :title="$t('contents.tipBtnApplyChanges')"
            :disabled="!compareResource.contents?.length"
            @click="copyFromComparison"
          >
            <template #icon>
              <n-icon :component="MoveDownIcon" />
            </template>
          </n-button>
          <n-button
            secondary
            :title="$t('contents.tipBtnNextChange')"
            @click="() => handleNearestChangeClick('after')"
          >
            <template #icon>
              <n-icon :component="SkipNextIcon" />
            </template>
          </n-button>
        </button-shelf>
      </n-alert>

      <!-- CORRECTION NOTES -->
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
              @prev-click="() => gotoLocation(prevCorrection?.locationId)"
              @next-click="() => gotoLocation(nextCorrection?.locationId)"
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
    :allow-level-change="false"
    @submit="(locPath) => gotoLocation(locPath[locPath.length - 1].id)"
  />
</template>

<style scoped>
:deep(.corrections > .n-collapse-item .n-collapse-item__content-inner) {
  padding-top: 0;
}
</style>
