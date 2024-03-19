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
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import type { AdvancedSearchRequestBody, ResourceType } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import type { SelectMixedOption } from 'naive-ui/es/select/src/interface';
import CommonSearchFormItems from '@/forms/resources/search/CommonSearchFormItems.vue';
import { $t } from '@/i18n';
import { useRouter } from 'vue-router';
import { useResourcesStore, useSearchStore } from '@/stores';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';

const search = useSearchStore();
const resources = useResourcesStore();
const router = useRouter();
const themeVars = useThemeVars();

const queries = ref<AdvancedSearchRequestBody['q']>([]);

const resourceOptions = computed(() =>
  resources.data.map((r) => ({
    label: `${r.title} (${$t('resources.types.' + r.resourceType + '.label')})`,
    value: r.id,
    resourceType: r.resourceType,
  }))
);

function handleResourceChange(resQueryIndex: number, resId: string, resType: ResourceType) {
  if (!queries.value[resQueryIndex]) return;
  if (queries.value[resQueryIndex].cmn.res !== resId) {
    queries.value[resQueryIndex] = {
      cmn: { res: resId, opt: true },
      rts: { ...queries.value[resQueryIndex].rts, type: resType },
    };
  }
}

function getNewSearchItem(): AdvancedSearchRequestBody['q'][number] {
  return {
    cmn: { res: resources.data[0].id, opt: true },
    rts: { type: resources.data[0].resourceType },
  };
}

function addSearchItem(index: number) {
  queries.value.splice(index + 1, 0, getNewSearchItem());
}

function removeSearchItem(index: number) {
  queries.value.splice(index, 1);
}

function handleSearch(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  router.push({
    name: 'searchResults',
    query: {
      q: search.encodeQueryParam({
        type: 'advanced',
        q: queries.value,
        gen: search.settingsGeneral,
        adv: search.settingsAdvanced,
      }),
    },
  });
}

function initQueries() {
  if (search.lastReq?.type === 'advanced') {
    queries.value = search.lastReq.q;
  } else {
    queries.value = resources.data.length ? [getNewSearchItem()] : [];
  }
}

watch(
  () => resources.data,
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
      <div class="gray-box">
        <general-search-settings-form />
      </div>
    </n-collapse-item>
  </n-collapse>

  <n-form
    v-if="!!resources.data.length"
    :model="queries"
    label-placement="top"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <n-dynamic-input
      v-model:value="queries"
      :min="1"
      :max="32"
      item-class="advanced-search-item"
      item-style="flex-direction: column; margin: 0"
      @create="getNewSearchItem"
    >
      <!-- SEARCH ITEM -->
      <template #default="{ value: resourceQuery, index }">
        <div style="flex-grow: 2" class="search-item content-block">
          <n-form-item :show-label="false" style="flex-grow: 2">
            <n-select
              :value="resourceQuery.cmn.res"
              :options="resourceOptions"
              :consistent-menu-width="false"
              size="large"
              @update:value="
                (v, o: SelectMixedOption) =>
                  handleResourceChange(index, v, o.resourceType as ResourceType)
              "
            />
          </n-form-item>
          <component
            :is="resourceTypeSearchForms[resourceQuery.rts.type]"
            v-model:value="resourceQuery.rts"
          />
          <common-search-form-items
            v-model:comment="resourceQuery.cmn.cmt"
            v-model:optional="resourceQuery.cmn.opt"
          />
          <div class="search-item-action-buttons">
            <n-button
              v-if="queries.length < 32"
              circle
              :color="themeVars.bodyColor"
              :style="{ color: themeVars.textColor1 }"
              :title="$t('general.insertAction')"
              :focusable="false"
              class="action-button-insert"
              @click="addSearchItem(index)"
            >
              <n-icon :component="AddIcon" />
            </n-button>
            <n-button
              v-if="queries.length > 1"
              circle
              :color="themeVars.bodyColor"
              :style="{ color: themeVars.textColor1 }"
              :title="$t('general.removeAction')"
              :focusable="false"
              class="action-button-remove"
              @click="removeSearchItem(index)"
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

  <button-shelf v-if="!!resources.data.length" top-gap>
    <n-button type="primary" :disabled="!queries.length" @click="handleSearch">
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
  gap: var(--layout-gap);
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
</style>
