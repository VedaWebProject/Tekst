<script setup lang="ts">
import { GET } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import NInputOsk from '@/components/NInputOsk.vue';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import QuickSearchSettingsForm from '@/forms/search/QuickSearchSettingsForm.vue';
import { $t } from '@/i18n';
import { ResourceIcon, SearchIcon, SettingsIcon } from '@/icons';
import { useResourcesStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import { NButton, NIcon, NPopselect, type InputInst, type SelectOption } from 'naive-ui';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

const emit = defineEmits(['submit']);

const state = useStateStore();
const theme = useThemeStore();
const search = useSearchStore();
const resources = useResourcesStore();
const router = useRouter();

const showLocationSelect = ref(false);
const showSettingsModal = ref(false);
const showTargetResourcesModal = ref(false);
const loading = ref(false);
const quickSearchInputRef = ref<InputInst | null>(null);

const tooltip = computed(() => {
  const targetTxtTitles = !!search.settingsQuick.txt?.length
    ? state.pf?.texts
        .filter((t) => search.settingsQuick.txt?.includes(t.id))
        .map((t) => `"${t.title}"`)
        .join(', ')
    : $t('search.settings.quick.textsPlaceholder');
  return `${$t('search.quickSearch.title')} ${$t('general.in')}: ${targetTxtTitles}`;
});

const locationSelectOptions = ref<SelectOption[]>([]);

const searchableResources = computed(
  () =>
    (search.settingsQuick.txt?.length
      ? search.settingsQuick.txt
      : state.pf?.texts.map((t) => t.id)
    )?.map((tId) => ({
      title: state.textById(tId)?.title,
      color: theme.getAccentColors(tId).base,
      resources: resources.all.filter((r) => r.textId === tId && r.config.common.searchableQuick),
    })) || []
);

async function handleSearch() {
  loading.value = true;
  const matchesToShow = 10;

  // check if the input matches a location alias
  const { data, error } = await GET('/locations', {
    params: {
      query: {
        textId: state.text?.id || '',
        alias: search.queryQuick,
        limit: matchesToShow,
      },
    },
  });

  if (!error && !!data.length) {
    if (data.length === 1 && !!state.pf?.state.directJumpOnUniqueAliasSearch) {
      // there is one matching location alias, so we directly navigate to this location
      router.push({
        name: 'browse',
        params: { textSlug: state.text?.slug || '', locId: data[0].id },
      });
    } else {
      // there are multiple matching locations, so we show a list of them
      locationSelectOptions.value = [
        {
          type: 'group',
          label: $t('browse.location.goTo'),
          children: [
            ...data.map((l) => ({
              type: 'location',
              label: l.label + (l.full ? ` (${l.full})` : ''),
              value: l.id,
            })),
            ...(data.length === matchesToShow
              ? [
                  {
                    label: '...',
                    value: '...',
                    disabled: true,
                  },
                ]
              : []),
          ],
        },
        {
          type: 'group',
          label: $t('search.searchAction'),
          children: [
            {
              type: 'search',
              label: search.queryQuick,
              value: search.queryQuick,
            },
          ],
        },
      ];
      showLocationSelect.value = true;
    }
  } else {
    // there is no matching location alias, so we perform a quick search using the input
    quickSearch(search.queryQuick);
  }

  loading.value = false;

  if (!state.smallScreen) {
    quickSearchInputRef.value?.select();
  } else {
    quickSearchInputRef.value?.blur();
  }
}

function handleSelect(value: string, option: SelectOption) {
  if (option.type === 'location') {
    router.push({
      name: 'browse',
      params: { textSlug: state.text?.slug || '', locId: option.value },
    });
    emit('submit', search.queryQuick);
  } else if (option.type === 'search') {
    quickSearch(value);
  }
  showLocationSelect.value = false;
  locationSelectOptions.value = [];
}

function quickSearch(q: string) {
  search.searchQuick(q);
  emit('submit', search.queryQuick);
}
</script>

<template>
  <div v-bind="$attrs">
    <n-popselect
      trigger="manual"
      :show="showLocationSelect"
      :options="locationSelectOptions"
      width="trigger"
      @update:value="handleSelect"
      @clickoutside="showLocationSelect = false"
    >
      <n-input-osk
        ref="quickSearchInputRef"
        v-model="search.queryQuick"
        round
        :placeholder="$t('search.quickSearch.title')"
        :title="tooltip"
        :max-length="512"
        :loading="loading"
        @input="showLocationSelect = false"
        @keydown.enter.stop.prevent="handleSearch"
      >
        <template #prefix>
          <n-icon :component="SearchIcon" />
        </template>
        <template #suffix>
          <n-button
            text
            :title="$t('general.settings')"
            :focusable="false"
            @click.stop.prevent="
              () => {
                quickSearchInputRef?.blur();
                showSettingsModal = true;
              }
            "
          >
            <template #icon>
              <n-icon :component="SettingsIcon" />
            </template>
          </n-button>
          <help-button-widget help-key="quickSearch" @click="quickSearchInputRef?.blur()" />
        </template>
      </n-input-osk>
    </n-popselect>
  </div>

  <generic-modal
    v-model:show="showSettingsModal"
    :title="`${$t('search.quickSearch.title')}: ${$t('general.settings')}`"
    :icon="SettingsIcon"
  >
    <general-search-settings-form />
    <quick-search-settings-form @target-resources-click="showTargetResourcesModal = true" />

    <button-shelf>
      <n-button type="primary" @click="showSettingsModal = false">
        {{ $t('general.okAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>

  <generic-modal
    v-model:show="showTargetResourcesModal"
    :title="$t('search.settings.quick.targetResources')"
    :icon="ResourceIcon"
    width="wide"
  >
    <template v-for="(txt, index) in searchableResources" :key="`${txt.title}_${index}`">
      <h3 :style="{ color: txt.color }">{{ txt.title }}</h3>
      <ul class="m-0">
        <li v-for="res in txt.resources" :key="res.id">
          {{ resources.resourceTitles[res.id] }}
        </li>
      </ul>
    </template>
  </generic-modal>
</template>
