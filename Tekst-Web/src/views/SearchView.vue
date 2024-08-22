<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { AddIcon, ClearIcon, NoContentIcon, SearchIcon } from '@/icons';
import { resourceTypeSearchForms } from '@/forms/resources/search/mappings';
import {
  NCollapse,
  NCollapseItem,
  NForm,
  NButton,
  NDynamicInput,
  NIcon,
  NSelect,
  NFormItem,
  useThemeVars,
  type FormInst,
} from 'naive-ui';
import { computed, h, ref, watch } from 'vue';
import type { AdvancedSearchRequestBody, AnyResourceRead, ResourceType } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import type { SelectMixedOption } from 'naive-ui/es/select/src/interface';
import CommonSearchFormItems from '@/forms/resources/search/CommonSearchFormItems.vue';
import { $t } from '@/i18n';
import { useRouter } from 'vue-router';
import { useResourcesStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import { useMessages } from '@/composables/messages';
import { pickTranslation } from '@/utils';
import { usePlatformData } from '@/composables/platformData';

type AdvancedSearchRequestQuery = AdvancedSearchRequestBody['q'][number];
interface AdvancedSearchFormModelItem extends AdvancedSearchRequestQuery {
  resource?: AnyResourceRead;
}
interface AdvancedSearchFormModel {
  queries: AdvancedSearchFormModelItem[];
}

const state = useStateStore();
const { pfData } = usePlatformData();
const search = useSearchStore();
const resources = useResourcesStore();
const router = useRouter();
const theme = useThemeStore();
const themeVars = useThemeVars();
const { message } = useMessages();

const formModel = ref<AdvancedSearchFormModel>({ queries: [] });
const formRef = ref<FormInst | null>(null);

const resourceOptions = computed(() => {
  const textIds = [
    ...(state.text?.id ? [state.text?.id] : []),
    ...[...new Set(resources.all.map((r) => r.textId))].filter((tId) => tId !== state.text?.id),
  ];
  return textIds.map((tId) => ({
    type: 'group',
    render: () =>
      h(
        'div',
        {
          class: 'text-tiny b',
          style: {
            color: theme.generateAccentColorVariants(state.textsProps[tId].accentColor).base,
            padding: '8px',
          },
        },
        state.textsProps[tId].title
      ),
    key: tId,
    children: resources.all
      .filter((r) => r.textId === tId)
      .sort((a, b) => {
        const categories =
          pfData.value?.texts
            .find((t) => t.id === a.textId)
            ?.resourceCategories?.map((c) => c.key) || [];
        const catA = categories.includes(a.config?.common?.category || '')
          ? categories.indexOf(a.config?.common?.category || '')
          : 99;
        const catB = categories.includes(b.config?.common?.category || '')
          ? categories.indexOf(b.config?.common?.category || '')
          : 99;
        const soA = a.config?.common?.sortOrder || 99;
        const soB = b.config?.common?.sortOrder || 99;
        return catA * 100 + soA - (catB * 100 + soB);
      })
      .map((r) => ({
        label: `${pickTranslation(r.title, state.locale)} – ${$t('resources.types.' + r.resourceType + '.label')}`,
        value: r.id,
        resourceType: r.resourceType,
        textColor: state.textsProps[tId].accentColor,
        textTitle: state.textsProps[tId].title,
      })),
  }));
});

function handleResourceChange(resQueryIndex: number, resId: string, resType: ResourceType) {
  if (!formModel.value.queries[resQueryIndex]) return;
  if (formModel.value.queries[resQueryIndex].cmn.res !== resId) {
    formModel.value.queries[resQueryIndex] = {
      cmn: { res: resId, opt: true },
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
    cmn: { res: resource.id, opt: true },
    rts: { type: resource.resourceType },
    resource: resource,
  };
}

function addSearchItem(index: number) {
  formModel.value.queries.splice(index + 1, 0, getNewSearchItem());
}

function removeSearchItem(index: number) {
  formModel.value.queries.splice(index, 1);
}

function handleSearch(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      router.push({
        name: 'searchResults',
        query: {
          q: search.encodeQueryParam({
            type: 'advanced',
            q: formModel.value.queries.map((q) => {
              // eslint-disable-next-line @typescript-eslint/no-unused-vars
              const { resource, ...query } = q; // remove "resource" q
              return query;
            }),
            gen: search.settingsGeneral,
            adv: search.settingsAdvanced,
          }),
        },
      });
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

function initQueries() {
  if (search.lastReq?.type === 'advanced') {
    formModel.value.queries = search.lastReq.q.map((q) => ({
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
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ $t('search.heading') }}
    <help-button-widget help-key="searchView" />
  </icon-heading>

  <n-collapse>
    <n-collapse-item :title="$t('search.settings.heading')" name="settings">
      <div class="gray-box mb-lg">
        <general-search-settings-form />
      </div>
    </n-collapse-item>
  </n-collapse>

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
      item-class="advanced-search-item"
      item-style="flex-direction: column; margin: 0"
      @create="getNewSearchItem"
    >
      <!-- SEARCH ITEM -->
      <template #default="{ value: query, index: queryIndex }">
        <div style="flex-grow: 2" class="search-item content-block">
          <n-form-item :show-label="false" style="flex-grow: 2">
            <n-select
              class="search-resource-select"
              :value="query.cmn.res"
              :options="resourceOptions"
              :consistent-menu-width="false"
              :menu-props="{ class: 'search-resource-select-menu' }"
              size="large"
              style="font-weight: var(--font-weight-bold)"
              :style="{
                color: theme.generateAccentColorVariants(
                  state.textsProps[query.resource?.textId]?.accentColor
                ).base,
              }"
              @update:value="
                (v, o: SelectMixedOption) =>
                  handleResourceChange(queryIndex, v, o.resourceType as ResourceType)
              "
            />
          </n-form-item>
          <component
            :is="resourceTypeSearchForms[query.rts.type]"
            v-model="query.rts"
            :resource="query.resource"
            :query-index="queryIndex"
          />
          <common-search-form-items
            v-model:comment="query.cmn.cmt"
            v-model:optional="query.cmn.opt"
            :query-index="queryIndex"
          />
          <div class="search-item-action-buttons">
            <n-button
              v-if="formModel.queries.length < 32"
              circle
              :color="themeVars.bodyColor"
              :style="{ color: themeVars.textColor1 }"
              :title="$t('general.insertAction')"
              :focusable="false"
              class="action-button-insert"
              @click="addSearchItem(queryIndex)"
            >
              <n-icon :component="AddIcon" />
            </n-button>
            <n-button
              v-if="formModel.queries.length > 1"
              circle
              :color="themeVars.bodyColor"
              :style="{ color: themeVars.textColor1 }"
              :title="$t('general.removeAction')"
              :focusable="false"
              class="action-button-remove"
              @click="removeSearchItem(queryIndex)"
            >
              <n-icon :component="ClearIcon" />
            </n-button>
          </div>
        </div>
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
    <n-button type="primary" :disabled="!formModel.queries.length" @click="handleSearch">
      {{ $t('search.searchAction') }}
    </n-button>
  </button-shelf>
</template>

<style scoped>
.search-item {
  position: relative;
}

.search-item-action-buttons {
  position: absolute;
  left: 0;
  bottom: -16px;
  width: 100%;
  display: flex;
  flex-wrap: nowrap;
  justify-content: center;
  gap: var(--gap-lg);
}
.search-item-action-buttons .action-button-insert:hover {
  color: var(--col-success) !important;
}
.search-item-action-buttons .action-button-remove:hover {
  color: var(--col-error) !important;
}
.search-item-action-button-wrapper {
  border-radius: 3px;
}
.search-resource-select :deep(.n-base-selection .n-base-selection-label .n-base-selection-input) {
  color: inherit;
}
</style>

<style>
.search-resource-select-menu.n-base-select-menu
  .n-base-select-option.n-base-select-option--selected,
.search-resource-select-menu.n-base-select-menu
  .n-base-select-option.n-base-select-option--selected
  .n-base-select-option__check {
  color: unset;
  font-weight: var(--font-weight-bold);
}
</style>
