<script setup lang="ts">
import { computed } from 'vue';
import { NAffix, NButton } from 'naive-ui';
import { useRoute } from 'vue-router';
import TextLocation from '@/components/browse/TextLocation.vue';
import LayersRound from '@vicons/material/LayersRound';
import { useStateStore } from '@/stores';

const route = useRoute();
const state = useStateStore();

const textLevelLabel = computed(() => state.text?.levels[state.browse?.level || 0]);
</script>

<template>
  <div v-if="route.name == 'browse'" class="browse-toolbar-container">
    <n-affix :top="0" class="browse-toolbar-affix accent-color-bg">
      <div class="browse-toolbar">
        <TextLocation />
        <div class="text-location-label">{{ textLevelLabel }}: {{ state.browse?.label }}</div>
        <n-button secondary size="large" color="#fffe">
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
}
.browse-toolbar-affix {
  width: 100%;
  max-width: var(--max-app-width);
  height: var(--browse-toolbar-height);
  border-radius: var(--app-ui-border-radius);
  box-shadow: var(--app-ui-block-box-shadow);
}

.browse-toolbar-affix.n-affix--affixed {
  border-top-left-radius: 0px;
  border-top-right-radius: 0px;
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

.browse-toolbar .text-location-label {
  flex-grow: 2;
}
</style>
