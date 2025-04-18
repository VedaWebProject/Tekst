<script setup lang="ts">
import { type AnyResourceRead, type ResourceSearchQuery, type SearchableResourceType } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import CommonSearchFormItems from '@/forms/resources/search/CommonSearchFormItems.vue';
import SearchOccurrenceSelector from '@/forms/resources/search/SearchOccurrenceSelector.vue';
import { resourceTypeSearchForms } from '@/forms/resources/search/mappings';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import { $t } from '@/i18n';
import { AddIcon, ClearIcon, LevelsIcon, NoContentIcon, SearchIcon } from '@/icons';
import { useResourcesStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { useMagicKeys, whenever } from '@vueuse/core';
import {
  NButton,
  NDynamicInput,
  NFlex,
  NForm,
  NFormItem,
  NIcon,
  NSelect,
  NTag,
  type FormInst,
} from 'naive-ui';
import type { SelectMixedOption, SelectOption } from 'naive-ui/es/select/src/interface';
import { computed, h, ref, watch, type VNodeChild } from 'vue';

interface AdvancedSearchFormModelItem extends ResourceSearchQuery {
  resource?: AnyResourceRead;
}
interface AdvancedSearchFormModel {
  queries: AdvancedSearchFormModelItem[];
}

const state = useStateStore();
const theme = useThemeStore();
const search = useSearchStore();
const resources = useResourcesStore();
const { message } = useMessages();

const formModel = ref<AdvancedSearchFormModel>({ queries: [] });
const formRef = ref<FormInst | null>(null);

const searchHeading = computed(
  () => pickTranslation(state.pf?.state.navSearchEntry, state.locale) || $t('common.search')
);

const resourceOptions = computed(() => {
  const textIds = [
    ...(state.text?.id ? [state.text?.id] : []),
    ...(state.pf?.texts.map((t) => t.id).filter((tId) => tId !== state.text?.id) || []),
  ];
  return textIds.map((tId) => ({
    type: 'group',
    render: () =>
      h(
        'div',
        {
          class: 'text-small b',
          style: {
            color: theme.getAccentColors(tId).base,
            padding: '8px',
          },
        },
        state.textById(tId)?.title || ''
      ),
    key: tId,
    children: resources.all
      .filter((r) => r.textId === tId)
      .filter((r) => r.config.general.searchableAdv)
      .sort((a, b) => {
        const categories =
          state.pf?.texts.find((t) => t.id === a.textId)?.resourceCategories?.map((c) => c.key) ||
          [];
        const catA = categories.includes(a.config.general.category || '')
          ? categories.indexOf(a.config.general.category || '')
          : 99;
        const catB = categories.includes(b.config.general.category || '')
          ? categories.indexOf(b.config.general.category || '')
          : 99;
        const soA = a.config.general.sortOrder || 99;
        const soB = b.config.general.sortOrder || 99;
        return catA * 100 + soA - (catB * 100 + soB);
      })
      .map((r) => ({
        label: pickTranslation(r.title, state.locale),
        value: r.id,
        resourceType: r.resourceType,
        textColor: theme.getAccentColors(tId).base,
        level: r.level,
      })),
  }));
});

const resourceColors = computed(() =>
  Object.fromEntries(resources.all.map((r) => [r.id, { colors: theme.getAccentColors(r.textId) }]))
);

function renderResourceOptionLabel(option: SelectOption): VNodeChild {
  return h(
    NFlex,
    { align: 'center', justify: 'space-between', wrap: false, class: 'mr-lg' },
    () => [
      h('span', { style: 'white-space: nowrap' }, option.label as string),
      !state.smallScreen &&
        h(
          NTag,
          { size: 'small', style: 'cursor: pointer; font-weight: normal' },
          {
            default: () => state.textLevelLabels[option.level as number],
            icon: () => h(NIcon, { component: LevelsIcon }),
          }
        ),
    ]
  );
}

function handleResourceChange(
  resQueryIndex: number,
  resId: string,
  resType: SearchableResourceType
) {
  if (!formModel.value.queries[resQueryIndex]) return;
  if (formModel.value.queries[resQueryIndex].cmn.res !== resId) {
    formModel.value.queries[resQueryIndex] = {
      cmn: { res: resId, occ: formModel.value.queries[resQueryIndex].cmn.occ || 'must' },
      rts: { type: resType },
      resource: resources.all.find((r) => r.id === resId),
    };
  }
}

function getNewSearchItem(): AdvancedSearchFormModelItem {
  const resId =
    resourceOptions.value.find((ro) => ro.key === state.text?.id)?.children[0]?.value ||
    resources.ofText[0].id;
  const resource = resources.all.find((r) => r.id === resId) || resources.ofText[0];
  return {
    cmn: { res: resource.id, occ: 'must' },
    rts: { type: resource.resourceType as SearchableResourceType },
    resource: resource,
  };
}

function addSearchItem(index: number) {
  formModel.value.queries.splice(index + 1, 0, getNewSearchItem());
}

function removeSearchItem(index: number) {
  formModel.value.queries.splice(index, 1);
}

function handleSearch() {
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      search.searchAdvanced(
        formModel.value.queries.map((q) => {
          const { resource, ...query } = q; // remove "resource" prop from q
          return query;
        })
      );
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

function initQueries() {
  if (search.currentRequest?.type === 'advanced') {
    formModel.value.queries = search.currentRequest.q.map((q) => ({
      ...q,
      resource: resources.all.find((r) => r.id === q.cmn.res),
    }));
  } else {
    formModel.value.queries = resources.all.length ? [getNewSearchItem()] : [];
  }
}

watch(
  () => resources.dataHash,
  () => {
    initQueries();
  },
  { immediate: true }
);

// search on Ctrl+Enter
const keys = useMagicKeys();
const ctrlEnter = keys['Ctrl+Enter'];
whenever(ctrlEnter, () => {
  handleSearch();
});
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ searchHeading }}
    <help-button-widget help-key="searchView" />
  </icon-heading>

  <general-search-settings-form />

  <n-form
    v-if="!!resources.all.length"
    ref="formRef"
    :model="formModel"
    label-placement="top"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <n-dynamic-input
      v-model:value="formModel.queries"
      :min="1"
      :max="32"
      item-class="search-item my-md"
      :create-button-props="dynInputCreateBtnProps"
      @create="getNewSearchItem"
    >
      <!-- SEARCH ITEM -->
      <template #default="{ value: query, index: queryIndex }">
        <div class="content-block p-0">
          <n-flex
            :wrap="false"
            class="search-item-header p"
            :style="{ backgroundColor: resourceColors[query.cmn.res].colors.fade3 }"
          >
            <n-flex align="flex-start" style="flex: 2">
              <n-form-item :show-label="false" :show-feedback="false" style="flex: 6 400px">
                <n-select
                  class="search-resource-select b"
                  :value="query.cmn.res"
                  :options="resourceOptions"
                  :consistent-menu-width="false"
                  :menu-props="{ class: 'search-resource-select-menu' }"
                  :render-label="renderResourceOptionLabel"
                  @update:value="
                    (v, o: SelectMixedOption) =>
                      handleResourceChange(queryIndex, v, o.resourceType as SearchableResourceType)
                  "
                />
              </n-form-item>
              <search-occurrence-selector
                v-model:occurrence="query.cmn.occ"
                :query-index="queryIndex"
                style="flex: 1 180px"
              />
            </n-flex>
            <n-button
              v-if="formModel.queries.length > 1"
              quaternary
              circle
              :title="$t('common.remove')"
              :focusable="false"
              class="action-button-remove"
              @click="removeSearchItem(queryIndex)"
            >
              <n-icon :component="ClearIcon" />
            </n-button>
          </n-flex>
          <div class="p">
            <component
              :is="resourceTypeSearchForms[query.rts.type]"
              v-model="query.rts"
              :resource="query.resource"
              :query-index="queryIndex"
            />
            <common-search-form-items v-model:comment="query.cmn.cmt" :query-index="queryIndex" />
          </div>
        </div>
        <n-button
          v-if="formModel.queries.length < 32 && queryIndex === formModel.queries.length - 1"
          secondary
          :title="$t('common.insert')"
          :focusable="false"
          class="mt-lg"
          @click="addSearchItem(queryIndex)"
        >
          <template #icon>
            <n-icon :component="AddIcon" />
          </template>
          {{ $t('search.advancedSearch.addQuery') }}
        </n-button>
      </template>
      <!-- ADD / REMOVE ACTION BUTTONS -->
      <template #action>
        <div>
          <!-- this is needed so the default action buttons don't show -->
        </div>
      </template>
    </n-dynamic-input>
  </n-form>

  <huge-labelled-icon
    v-else
    :message="$t('search.advancedSearch.msgNoResources')"
    :icon="NoContentIcon"
  />

  <button-shelf v-if="!!resources.all.length" top-gap>
    <n-button
      type="primary"
      :title="`${$t('common.searchAction')} (${$t('common.ctrlEnter')})`"
      :disabled="!formModel.queries.length"
      @click.stop.prevent="handleSearch"
    >
      {{ $t('common.searchAction') }}
    </n-button>
  </button-shelf>
</template>

<style scoped>
:deep(.search-item) {
  position: relative;
  flex-direction: column;
  margin: 1rem 0;
}

:deep(.search-item > .content-block) {
  margin: 0;
}

:deep(.search-item .search-item-header) {
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
}
</style>

<style>
.search-resource-select-menu.n-base-select-menu
  .n-base-select-option.n-base-select-option--selected,
.search-resource-select-menu.n-base-select-menu
  .n-base-select-option.n-base-select-option--selected
  .n-base-select-option__check {
  color: unset;
  font-weight: bold;
}

.search-resource-select-menu .n-base-select-option .n-base-select-option__content {
  width: 100%;
}
</style>
