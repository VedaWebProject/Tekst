<script setup lang="ts">
import NavBar from '@/components/NavBar.vue';
import { NButton, NIcon } from 'naive-ui';
import ArrowDropDownFilled from '@vicons/material/ArrowDropDownFilled';
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>
  <header>
    <NavBar />
    <div id="current-text-container">
      <div id="current-text">
        <n-button text icon-placement="right" color="#fff">
          <template #icon>
            <n-icon>
              <ArrowDropDownFilled />
            </n-icon>
          </template>
          {{ state.text?.title || 'Text state not implemented' }}
        </n-button>
      </div>
    </div>
  </header>
</template>

<style scoped>
#current-text-container {
  background-color: var(--accent-color);
  color: #fff;
}

#current-text {
  padding: var(--layout-padding);
  max-width: var(--max-app-width);
  margin: 0 auto;
}
</style>
