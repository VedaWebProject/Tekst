<script setup lang="ts">
import { computed } from 'vue';
import { NAffix, NButton } from 'naive-ui';
import BrowseLocation from '@/components/browse/BrowseLocation.vue';
import LayersRound from '@vicons/material/LayersRound';
import { useStateStore, useBrowseStore } from '@/stores';

const state = useStateStore();
const browse = useBrowseStore();

const showBrowseToolbar = computed(() => !!state.text);
const browseLocationLabel = computed(() =>
  browse.nodePath
    .map((n, i) => {
      return `${state.text?.labeledLevels ? state.text?.levels[i] : ''}${
        state.text?.labeledLevels ? ': ' : ''
      }${n.label}`;
    })
    .join(state.text?.locDelim || ', ')
);
</script>

<template>
  <div v-if="showBrowseToolbar" class="browse-toolbar-container">
    <n-affix :top="0" class="browse-toolbar-affix accent-color-bg">
      <div class="browse-toolbar">
        <BrowseLocation />
        <div class="text-location-label">
          {{ browseLocationLabel }}
        </div>
        <n-button secondary size="large" color="#fffe" :focusable="false">
          <template #icon>
            <LayersRound />
          </template>
        </n-button>
      </div>
    </n-affix>
  </div>
</template>

<style scoped>
.browse-toolbar-container {
  --browse-toolbar-height: 64px;
  height: var(--browse-toolbar-height);
  border-radius: var(--app-ui-border-radius);
  box-shadow: var(--app-ui-block-box-shadow);
}
.browse-toolbar-affix {
  width: 100%;
  max-width: var(--max-app-width);
  height: var(--browse-toolbar-height);
  border-radius: var(--app-ui-border-radius);
  box-shadow: var(--app-ui-block-box-shadow);
  transition: none;
}

.browse-toolbar-affix.n-affix--affixed {
  border-radius: unset;
  max-width: unset;
  width: 100vw;
  left: 0px;
  box-shadow: var(--app-ui-fixed-box-shadow);
}

.browse-toolbar {
  height: var(--browse-toolbar-height);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin: 0 auto;
  padding: 0 var(--layout-padding);
}

.browse-toolbar-affix.n-affix--affixed .browse-toolbar {
  max-width: var(--max-app-width);
}

.browse-toolbar .text-location-label {
  flex-grow: 2;
}
</style>
