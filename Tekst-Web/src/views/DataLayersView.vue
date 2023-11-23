<script setup lang="ts">
import {
  NButton,
  NInput,
  NIcon,
  NCheckbox,
  NSpace,
  NSpin,
  NPagination,
  NList,
  useDialog,
} from 'naive-ui';
import { POST, type AnyLayerRead, type AnyLayerReadFull } from '@/api';
import { ref } from 'vue';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import LayerListItem from '@/components/LayerListItem.vue';
import { useLayers } from '@/fetchers';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import SearchRound from '@vicons/material/SearchRound';
import UndoRound from '@vicons/material/UndoRound';
import LayersFilled from '@vicons/material/LayersFilled';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import { useMessages } from '@/messages';

const state = useStateStore();
const auth = useAuthStore();
const dialog = useDialog();
const { message } = useMessages();

const textId = computed(() => state.text?.id || '');
const { layers, loading, error, load } = useLayers(textId);

const pagination = ref({
  page: 1,
  pageSize: 10,
});

const initialFilters = () => ({
  search: '',
  public: true,
  notPublic: true,
  proposed: true,
  notProposed: true,
  ownedByMe: true,
  ownedByOthers: true,
});

const filters = ref(initialFilters());

function filterData(layers: AnyLayerRead[]) {
  pagination.value.page = 1;
  return layers.filter((l) => {
    const layerStringContent = filters.value.search
      ? [l.title, l.description, l.ownerId, l.comment, l.citation, JSON.stringify(l.meta)]
          .filter((prop) => prop)
          .join(' ')
      : '';
    return (
      (!filters.value.search ||
        layerStringContent.toLowerCase().includes(filters.value.search.toLowerCase())) &&
      ((filters.value.proposed && l.proposed) || (filters.value.notProposed && !l.proposed)) &&
      ((filters.value.public && l.public) || (filters.value.notPublic && !l.public)) &&
      ((filters.value.ownedByMe && l.ownerId === auth.user?.id) ||
        (filters.value.ownedByOthers && l.ownerId !== auth.user?.id))
    );
  });
}

const filteredData = computed(() => filterData(layers.value || []));
const paginatedData = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  return filteredData.value.slice(start, end);
});

function handleProposeClick(layer: AnyLayerReadFull) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnPropose') + ' ' + $t('general.areYouSureHelpTextHint'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/propose', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('YAY'));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handleUnproposeClick(layer: AnyLayerReadFull) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnUnpropose'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/unpropose', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('YAY'));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handlePublishClick(layer: AnyLayerReadFull) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnPublish') + ' ' + $t('general.areYouSureHelpTextHint'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/publish', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('YAY'));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handleUnpublishClick(layer: AnyLayerReadFull) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnUnpublish'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/unpublish', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('YAY'));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handleEditClick(layer: AnyLayerReadFull) {
  alert('handleEditClick ' + JSON.stringify(layer));
}

function handleDeleteClick(layer: AnyLayerReadFull) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnDelete'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      alert('handleDeleteClick ' + JSON.stringify(layer));
    },
  });
}
</script>

<template>
  <IconHeading level="1" :icon="LayersFilled">
    {{ $t('dataLayers.heading') }} {{ layers ? `(${layers?.length})` : '' }}
    <HelpButtonWidget help-key="dataLayersView" />
  </IconHeading>

  <template v-if="layers && !error && !loading">
    <!-- Filters -->
    <div style="margin-bottom: 1.5rem">
      <n-input
        v-model:value="filters.search"
        :placeholder="$t('search.searchAction')"
        style="margin-bottom: 1rem"
        round
      >
        <template #prefix>
          <n-icon :component="SearchRound" />
        </template>
      </n-input>
      <n-space vertical justify="space-between" style="padding-left: 12px">
        <n-checkbox v-model:checked="filters.public" :label="$t('dataLayers.public')" />
        <n-checkbox v-model:checked="filters.notPublic" :label="$t('dataLayers.notPublic')" />
        <n-checkbox v-model:checked="filters.proposed" :label="$t('dataLayers.proposed')" />
        <n-checkbox v-model:checked="filters.notProposed" :label="$t('dataLayers.notProposed')" />
        <n-checkbox v-model:checked="filters.ownedByMe" :label="$t('dataLayers.ownedByMe')" />
        <n-checkbox
          v-model:checked="filters.ownedByOthers"
          :label="$t('dataLayers.ownedByOthers')"
        />
        <n-button
          secondary
          round
          style="margin-top: var(--layout-gap)"
          @click="filters = initialFilters()"
        >
          {{ $t('general.resetAction') }}
          <template #icon>
            <n-icon :component="UndoRound" />
          </template>
        </n-button>
      </n-space>
    </div>
    <!-- Layers List -->
    <div class="content-block">
      <template v-if="paginatedData.length > 0">
        <n-list style="background-color: transparent">
          <layer-list-item
            v-for="item in paginatedData"
            :key="item.id"
            :target-layer="item"
            :current-user="auth.user"
            @propose-click="handleProposeClick"
            @unpropose-click="handleUnproposeClick"
            @publish-click="handlePublishClick"
            @unpublish-click="handleUnpublishClick"
            @edit-click="handleEditClick"
            @delete-click="handleDeleteClick"
          />
        </n-list>
        <!-- Pagination -->
        <div style="display: flex; justify-content: flex-end; padding-top: 12px">
          <n-pagination
            v-model:page-size="pagination.pageSize"
            v-model:page="pagination.page"
            :page-sizes="[10, 20, 50, 100]"
            :default-page-size="10"
            :item-count="filteredData.length"
            show-size-picker
          />
        </div>
      </template>
      <template v-else>
        {{ $t('search.nothingFound') }}
      </template>
    </div>
  </template>

  <n-spin
    v-else-if="loading"
    size="large"
    style="margin: 3rem 0 2rem 0; width: 100%"
    :description="$t('init.loading')"
  />

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>
