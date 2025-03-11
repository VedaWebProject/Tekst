<script setup lang="ts">
import type { TextRead } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import TextSelectOption from '@/components/navigation/TextSelectOption.vue';
import { ExpandArrowDownIcon, InfoIcon, ResourceIcon, TextsIcon } from '@/icons';
import { useBrowseStore, useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NDropdown, NFlex, NIcon, NTag, useThemeVars } from 'naive-ui';
import { computed, h, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const state = useStateStore();
const browse = useBrowseStore();
const themeVars = useThemeVars();
const resources = useResourcesStore();

const disabled = computed(() => !state.pf?.texts || state.pf.texts.length <= 1);
const dropdownRef = ref();
const showInfoModal = ref(false);

const resourcesByLevel = computed(() =>
  state.textLevelLabels.map((_, i) => resources.ofText.filter((r) => r.level === i))
);

const renderLabel = (t: TextRead) => {
  return () =>
    h(TextSelectOption, {
      text: t,
      locale: state.locale,
      selected: t.id === state.text?.id,
      onClick: () => handleSelect(t),
    });
};

const options = computed(
  () =>
    state.pf?.texts.map((t: TextRead) => ({
      render: renderLabel(t),
      key: t.id,
      type: 'render',
      show: t.id !== state.text?.id,
    })) || []
);

function handleSelect(text: TextRead) {
  if (state.text?.id === text.id) return;
  dropdownRef.value.doUpdateShow(false);
  browse.locationPath = [];

  if (router.currentRoute.value.params.hasOwnProperty('textSlug')) {
    router.push({
      name: router.currentRoute.value.name,
      params: {
        ...router.currentRoute.value.params,
        textSlug: text.slug,
        locId: undefined,
      },
    });
  } else {
    state.text = state.textById(text.id);
  }
}
</script>

<template>
  <n-flex align="center" :wrap="false">
    <n-dropdown
      v-if="state.text"
      ref="dropdownRef"
      trigger="click"
      :options="options"
      :disabled="disabled"
      placement="bottom-start"
    >
      <n-button
        text
        icon-placement="right"
        :color="themeVars.baseColor"
        :focusable="false"
        :keyboard="false"
        :title="$t('general.textSelect')"
        class="text-select-btn"
        :style="{ cursor: !disabled ? 'pointer' : 'default' }"
      >
        <n-flex align="center" :wrap="false" style="max-width: 100%">
          <b class="text-title ellipsis text-large">{{ state.text.title }}</b>
          <n-icon v-if="!disabled" :component="ExpandArrowDownIcon" style="flex-shrink: 0" />
        </n-flex>
      </n-button>
    </n-dropdown>

    <n-button
      v-if="!state.smallScreen"
      quaternary
      circle
      color="var(--base-color)"
      :focusable="false"
      :keyboard="false"
      :title="$t('general.info')"
      @click="showInfoModal = true"
    >
      <template #icon>
        <n-icon :component="InfoIcon" />
      </template>
    </n-button>

    <generic-modal
      v-model:show="showInfoModal"
      :title="state.text?.title || $t('general.info')"
      :icon="TextsIcon"
      width="wide"
    >
      <h3>{{ $t('models.resource.modelLabel', 2) }} / {{ $t('models.text.level') }}</h3>
      <template
        v-for="(levelLabel, levelIndex) in state.textLevelLabels"
        :key="`level-${levelIndex}`"
      >
        <h4>{{ levelLabel }}</h4>
        <ul v-if="!!resourcesByLevel[levelIndex].length">
          <li v-for="res in resourcesByLevel[levelIndex]" :key="res.id">
            <n-flex align="center">
              <span>{{ pickTranslation(res.title, state.locale) }}</span>
              <n-tag size="small">
                <template #icon>
                  <n-icon :component="ResourceIcon" />
                </template>
                {{ $t(`resources.types.${res.resourceType}.label`) }}
              </n-tag>
            </n-flex>
          </li>
        </ul>
        <p v-else class="text-medium translucent i">
          {{ $t('texts.levels.noResources') }}
        </p>
      </template>
    </generic-modal>
  </n-flex>
</template>

<style scoped>
ul {
  margin-top: 0;
  padding-left: var(--gap-lg);
}

.text-select-btn {
  max-width: 100%;
  justify-content: flex-start;
}

.text-title {
  line-height: 150%;
  max-width: 100%;
}

.text-subtitle {
  max-width: 100%;
  line-height: 120%;
  padding-bottom: 0.2em;
}
</style>
