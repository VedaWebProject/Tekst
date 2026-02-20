<script setup lang="ts">
import {
  DELETE,
  downloadData,
  GET,
  PATCH,
  POST,
  withSelectedFile,
  type AnyResourceRead,
} from '@/api';
import { dialogProps } from '@/common';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ListingsFilters from '@/components/ListingsFilters.vue';
import SetResourceOwnersModal from '@/components/modals/SetResourceOwnersModal.vue';
import ResourceListItem from '@/components/resource/ResourceListItem.vue';
import { useMessages } from '@/composables/messages';
import { usePrompt } from '@/composables/prompt';
import { useTasks } from '@/composables/tasks';
import { $t } from '@/i18n';
import { AddIcon, JumpBackIcon, NoContentIcon, ResourceIcon, SearchIcon, UserIcon } from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore, useUserMessagesStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { useUrlSearchParams } from '@vueuse/core';
import { NButton, NCollapse, NEmpty, NIcon, NInput, NSpin, useDialog } from 'naive-ui';
import { computed, nextTick, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  textSlug?: string;
}>();

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();
const userMessages = useUserMessagesStore();
const dialog = useDialog();
const { message } = useMessages();
const router = useRouter();
const { addTask, startTasksPolling } = useTasks();
const hashParams = useUrlSearchParams('hash-params');
const prompt = usePrompt();

const actionsLoading = ref(false);
const loading = computed(() => actionsLoading.value || resources.loading);

const setResOwnersModalRef = ref<InstanceType<typeof SetResourceOwnersModal>>();

const filtersRef = ref<InstanceType<typeof ListingsFilters> | null>(null);
const searchInput = ref<string>();
const searchInputState = computed(() =>
  !!searchInput.value?.length && !filteredData.value.length
    ? 'error'
    : !!searchInput.value?.length
      ? 'warning'
      : undefined
);

function stringifyResourceProps(res: AnyResourceRead) {
  return [
    res.title.map((t) => t.translation).join(' '),
    res.subtitle.map((s) => s.translation).join(' ') || '',
    res.owners?.map((o) => o.name).join(' ') || '',
    res.owners?.map((o) => o.username).join(' ') || '',
    res.owners?.map((o) => o.affiliation).join(' ') || '',
    res.description.map((d) => d.translation).join(' ') || '',
    res.citation,
    ...res.meta.map(m => 'm:'+m.value),
    res.public ? $t('resources.public') : $t('resources.notPublic'),
    res.proposed ? $t('resources.proposed') : null,
    $t(`resources.types.${res.resourceType}.label`),
    state.textLevelLabels[res.level],
  ]
    .filter(Boolean)
    .join(' ').toLowerCase();
}

const filteredData = computed(() =>
  resources.ofText
    .filter(
      (r) =>
        !searchInput.value ||
        searchInput.value.toLowerCase().split(/[, ]+/).filter(Boolean).every(f => stringifyResourceProps(r).includes(f))
    )
    .sort((ra, rb) => {
      const correctionsComp = (rb.corrections ?? 0) - (ra.corrections ?? 0);
      const titleComp = pickTranslation(ra.title, state.locale).localeCompare(
        pickTranslation(rb.title, state.locale)
      );
      return correctionsComp || titleComp;
    })
);

const expandedNames = ref<string[]>([]);

async function handleBrowseClick(resource: AnyResourceRead) {
  router.push({
    name: 'browse',
    params: { textSlug: state.text?.slug || '' },
    hash: `#res=${resource.id}`,
  });
}

async function handleSetOwnersClick(resource: AnyResourceRead) {
  setResOwnersModalRef.value?.show(resource);
}

async function handleSetOwners(resource?: AnyResourceRead, newOwnerIds?: string[]) {
  if (!resource) return;
  actionsLoading.value = true;
  const { data, error } = await PATCH('/resources/{id}/owners', {
    params: { path: { id: resource.id } },
    body: newOwnerIds ?? [],
  });
  if (!error) {
    resources.replace(data);
    message.success(
      $t('resources.msgOwnersSet', {
        title: pickTranslation(resource.title, state.locale),
      })
    );
  }
  filtersRef.value?.reset();
  actionsLoading.value = false;
}

function handleProposeClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnPropose') + ' ' + $t('common.areYouSureHelpTextHint'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/propose', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgProposed', { title: pickTranslation(resource.title, state.locale) })
        );
      }
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handleUnproposeClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnUnpropose'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/unpropose', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgUnproposed', { title: pickTranslation(resource.title, state.locale) })
        );
      }
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handlePublishClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnPublish') + ' ' + $t('common.areYouSureHelpTextHint'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/publish', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgPublished', { title: pickTranslation(resource.title, state.locale) })
        );
      }
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handleUnpublishClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnUnpublish'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/unpublish', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgUnpublished', { title: pickTranslation(resource.title, state.locale) })
        );
      }
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handleSettingsClick(resource: AnyResourceRead) {
  router.push({
    name: 'resourceSettings',
    params: { textSlug: props.textSlug, id: resource.id },
  });
}

function handleEditContentsClick(resource: AnyResourceRead) {
  router.push({
    name: 'resourceContents',
    params: { textSlug: props.textSlug, resId: resource.id },
  });
}

function handleCreateVersionClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.information'),
    content: $t('resources.infoCreateVersion', {
      title: pickTranslation(resource.title, state.locale),
    }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/version', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.add(data);
        message.success(
          $t('resources.msgCreatedVersion', {
            title: pickTranslation(resource.title, state.locale),
          })
        );
        expandedNames.value = [data.id];
        nextTick(() => {
          document
            .querySelector(`#res-list-item-${data.id}`)
            ?.scrollIntoView({ behavior: 'smooth' });
        });
      }
      actionsLoading.value = false;
    },
  });
}

function handleDeleteClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnDelete'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { error } = await DELETE('/resources/{id}', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        message.success(
          $t('resources.msgDeleted', { title: pickTranslation(resource.title, state.locale) })
        );
      }
      await resources.load();
      actionsLoading.value = false;
    },
  });
}

async function handleDownloadTemplateClick(resource: AnyResourceRead) {
  actionsLoading.value = true;
  const { data, error } = await GET('/resources/{id}/template', {
    params: { path: { id: resource.id } },
    parseAs: 'blob',
  });
  if (!error) {
    const resSaveName = pickTranslation(resource.title, state.locale)
      .substring(0, 32)
      .trim()
      .replace(/\W+/g, '_');
    const filename = `${resSaveName}_${resource.id}_template.json`.toLowerCase();
    message.info($t('common.downloadSaved', { filename }));
    downloadData(data, filename);
  }
  actionsLoading.value = false;
}

async function handleImportClick(resource: AnyResourceRead) {
  withSelectedFile(async (file: File | null) => {
    if (!file) return;
    actionsLoading.value = true;
    const { data, error } = await POST('/resources/{id}/import', {
      params: { path: { id: resource.id } },
      body: { file },
      bodySerializer(body) {
        const fd = new FormData();
        for (const [k, v] of Object.entries(body)) {
          fd.append(k, v);
        }
        return fd;
      },
    });
    if (!error) {
      addTask(data);
      message.info($t('contents.msgImportInfo'), undefined, 5);
      startTasksPolling();
    }
    actionsLoading.value = false;
  });
}

async function handleReqVersionIntegrationClick(resourceVersion: AnyResourceRead) {
  const originalResource = resources.all.find((r) => r.id === resourceVersion.originalId);
  if (!originalResource || !originalResource.owners?.length) return;

  const contactOptions = originalResource.owners.map((o) => ({
    label: o.name ? `${o.name} (@${o.username})` : `@${o.username}`,
    value: o.id,
  }));
  const contactId = await prompt({
    type: 'select',
    icon: UserIcon,
    title: $t('resources.reqVersionIntegration.action'),
    msg: $t('resources.reqVersionIntegration.diagMsg'),
    label: $t('resources.reqVersionIntegration.diagLabel'),
    options: contactOptions,
    defaultValue: contactOptions[0]?.value,
  });

  if (!contactId) return;
  const versionTitle = pickTranslation(resourceVersion.title, state.locale);
  const originalTitle = pickTranslation(originalResource.title, state.locale);
  const prepMsg = `> ${versionTitle} → ${originalTitle}\n\n`;
  userMessages.openConversation(contactId, prepMsg);
}

function handleCollapseUpdate(activeItemName?: string) {
  // @ts-expect-error this is a valid property type but it's typed wrong in the library
  hashParams.id = activeItemName;
  setTimeout(
    () =>
      document
        .querySelector(`#res-list-item-${activeItemName}`)
        ?.scrollIntoView({ behavior: 'smooth' }),
    220
  );
}

onMounted(() => {
  // inform user in case there are corrections for resources of another text
  if (
    !resources.ofText.some((r) => !!r.corrections) &&
    resources.all.filter((r) => r.textId !== state.text?.id).some((r) => !!r.corrections)
  ) {
    message.info($t('resources.msgCorrections'));
  }

  // expand and scroll to the resource entry mentionen in the URL hash, if any
  nextTick(() => {
    if (hashParams.id) {
      const targetRes = resources.ofText.find((r) => r.id === hashParams.id);
      if (targetRes) {
        expandedNames.value = [targetRes.id];
        setTimeout(() => {
          document
            .querySelector(`#res-list-item-${targetRes.id}`)
            ?.scrollIntoView({ behavior: 'smooth' });
        }, 200);
      }
    }
  });
});
</script>

<template>
  <icon-heading level="1" :icon="ResourceIcon">
    {{ $t('resources.heading') }}
    <help-button-widget help-key="resourcesView" />
  </icon-heading>

  <template v-if="resources.ofText && !resources.error && !loading">
    <!-- Filter/Search -->
    <n-input
      v-model:value="searchInput"
      round
      clearable
      :status="searchInputState"
      :disabled="!resources.ofText.length"
      :placeholder="$t('resources.filterTip')"
      :title="$t('resources.filterTip')"
      class="mb-lg"
    >
      <template #prefix>
        <n-icon :component="SearchIcon" />
      </template>
    </n-input>

    <!-- List Header -->
    <button-shelf>
      <template #start>
        <div
          class="text-small translucent ellipsis"
          :style="{
            color:
              !!resources.ofText.length && !filteredData.length ? 'var(--error-color)' : undefined,
          }"
        >
          {{
            $t('resources.msgFoundCount', {
              count: filteredData.length,
              total: resources.ofText.length,
            })
          }}
        </div>
      </template>
      <!-- Reset filters button -->
      <n-button secondary :disabled="!searchInput?.length" @click="searchInput = ''">
        <template #icon>
          <n-icon :component="JumpBackIcon" />
        </template>
        {{ $t('common.reset') }}
      </n-button>
      <!-- Create new resource button -->
      <n-button
        v-if="auth.user"
        type="primary"
        @click="router.push({ name: 'resourceCreate', params: { textSlug: props.textSlug } })"
      >
        <template #icon>
          <n-icon :component="AddIcon" />
        </template>
        {{ $t('resources.new') }}
      </n-button>
    </button-shelf>

    <!-- Resources List -->
    <div class="content-block">
      <n-collapse
        v-if="filteredData.length"
        v-model:expanded-names="expandedNames"
        accordion
        class="my-sm"
        @update:expanded-names="(en: string[]) => handleCollapseUpdate(en[0])"
      >
        <resource-list-item
          v-for="item in filteredData"
          :id="`res-list-item-${item.id}`"
          :key="item.id"
          :resource="item"
          :user="auth.user"
          :shown="expandedNames.includes(item.id)"
          @browse-click="handleBrowseClick"
          @set-owners-click="handleSetOwnersClick"
          @propose-click="handleProposeClick"
          @unpropose-click="handleUnproposeClick"
          @publish-click="handlePublishClick"
          @unpublish-click="handleUnpublishClick"
          @settings-click="handleSettingsClick"
          @edit-contents-click="handleEditContentsClick"
          @create-version-click="handleCreateVersionClick"
          @delete-click="handleDeleteClick"
          @download-template-click="handleDownloadTemplateClick"
          @import-click="handleImportClick"
          @req-version-integration-click="handleReqVersionIntegrationClick"
        />
      </n-collapse>
      <n-empty v-else :description="$t('search.nothingFound')" class="my-lg">
        <template #icon>
          <n-icon :component="NoContentIcon" />
        </template>
      </n-empty>
    </div>
  </template>

  <n-spin v-else-if="loading" class="centered-spin" :description="$t('common.loading')" />

  <div v-else>
    {{ $t('errors.error') }}
  </div>

  <set-resource-owners-modal
    v-if="!!auth.user"
    ref="setResOwnersModalRef"
    :loading="actionsLoading"
    @submit="handleSetOwners"
  />
</template>

<style scoped>
.pagination-container:first-child {
  margin-bottom: var(--gap-lg);
}

.pagination-container:last-child {
  margin-top: var(--gap-lg);
}
</style>
