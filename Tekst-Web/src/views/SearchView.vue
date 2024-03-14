<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { AddIcon, MinusIcon, NoContentIcon, SearchIcon } from '@/icons';
import { resourceTypeSearchForms } from '@/forms/resources/search/mappings';
import {
  NForm,
  NButton,
  NButtonGroup,
  NDynamicInput,
  NSpace,
  NIcon,
  NSelect,
  NFormItem,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import type { AdvancedSearchRequestBody, ResourceType } from '@/api';
import { useResourcesStore, useStateStore } from '@/stores';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import type { SelectMixedOption } from 'naive-ui/es/select/src/interface';

const state = useStateStore();
const resources = useResourcesStore();

const initialSearchRequestModel: () => AdvancedSearchRequestBody = () => ({
  type: 'advanced',
  gen: state.searchSettingsGeneral,
  adv: state.searchSettingsAdvanced,
  q: [],
});
const reqModel = ref(initialSearchRequestModel());

const resourceOptions = computed(() =>
  resources.data.map((r) => ({ label: r.title, value: r.id, resourceType: r.resourceType }))
);

function handleResourceChange(resQueryIndex: number, resId: string, resType: ResourceType) {
  if (!reqModel.value.q[resQueryIndex]) return;
  if (reqModel.value.q[resQueryIndex].res !== resId) {
    reqModel.value.q[resQueryIndex] = {
      res: resId,
      type: resType,
    };
  }
}

watch(
  () => resources.data,
  () => {
    reqModel.value = initialSearchRequestModel();
  }
);
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ $t('search.heading') }}
    <help-button-widget help-key="searchView" />
  </icon-heading>

  <div class="content-block">
    <n-form v-if="!!resources.data.length">
      <n-dynamic-input
        v-model:value="reqModel.q"
        :min="1"
        :max="64"
        item-style="display: flex; flex-direction: column"
        @create="
          () => ({
            res: resources.data[0].id,
            type: resources.data[0].resourceType,
          })
        "
      >
        <template #default="{ value: resourceQuery, index }">
          <n-form-item :label="$t('models.resource.modelLabel')">
            <n-select
              :value="resourceQuery.res"
              :options="resourceOptions"
              @update:value="
                (v, o: SelectMixedOption) =>
                  handleResourceChange(index, v, o.resourceType as ResourceType)
              "
            />
          </n-form-item>
          <component
            :is="resourceTypeSearchForms[resourceQuery.type]"
            v-model:model="reqModel.q[index]"
          />
        </template>
        <template #action="{ index, create, remove }">
          <n-space style="flex-wrap: nowrap">
            <n-button-group>
              <n-button
                :title="$t('translationFormItem.tipBtnRemove')"
                :disabled="reqModel.q.length <= 1"
                @click="() => remove(index)"
              >
                <template #icon>
                  <n-icon :component="MinusIcon" />
                </template>
              </n-button>
              <n-button
                :title="$t('translationFormItem.tipBtnAdd')"
                :disabled="reqModel.q.length >= 64"
                @click="() => create(index)"
              >
                <template #icon>
                  <n-icon :component="AddIcon" />
                </template>
              </n-button>
            </n-button-group>
          </n-space>
        </template>
        <template #create-button-default>
          {{ $t('search.advancedSearch.btnAddSearchItem') }}
        </template>
      </n-dynamic-input>
    </n-form>

    <huge-labelled-icon
      v-else
      :message="$t('search.advancedSearch.msgNoResources')"
      :icon="NoContentIcon"
    />

    <button-shelf v-if="!!resources.data.length" top-gap>
      <n-button type="primary" :disabled="!reqModel.q.length">
        {{ $t('search.searchAction') }}
      </n-button>
    </button-shelf>
  </div>
</template>

<style scoped></style>
