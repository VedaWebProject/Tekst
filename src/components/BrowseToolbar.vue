<script setup lang="ts">
import { NAffix } from 'naive-ui';
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
  <div v-if="route.name == 'browse'" class="browse-toolbar-container">
    <n-affix :top="0" class="browse-toolbar-affix accent-color-bg">
      <div class="browse-toolbar">
        <div>FOO</div>
        <div>BAR</div>
        <div>BAZ</div>
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
  height: var(--browse-toolbar-height);
}
.browse-toolbar-affix.n-affix--affixed {
  box-shadow: 0px 12px 12px -12px rgba(0, 0, 0, 0.4);
}

.browse-toolbar {
  max-width: var(--max-app-width);
  height: var(--browse-toolbar-height);
  margin: 0 auto;
  padding: 0 var(--layout-padding);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
