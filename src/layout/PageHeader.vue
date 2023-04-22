<script setup lang="ts">
import PrimaryNavBar from '@/components/navigation/PrimaryNavBar.vue';
import TextSelect from '@/components/widgets/TextSelect.vue';
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>
  <header>
    <PrimaryNavBar />
    <div class="accent-color-bg">
      <div id="current-text">
        <TextSelect />
        <span v-if="!state.smallScreen" class="current-text-subtitle">
          {{ state.text?.subtitle }}
        </span>
      </div>
    </div>
  </header>
</template>

<style scoped>
#current-text {
  --current-text-height: 64px;
  height: var(--current-text-height);
  display: flex;
  column-gap: 24px;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--layout-padding);
  max-width: var(--max-app-width);
  margin: 0 auto;
  font-size: var(--app-ui-font-size-large);
}

#current-text .current-text-subtitle {
  font-weight: var(--app-ui-font-weight-light);
  filter: opacity(0.6);
}
</style>
