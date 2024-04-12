<script setup lang="ts">
import { NButton, NBadge, NFloatButton, NIcon } from 'naive-ui';
import { CheckCircleIcon, ErrorIcon, HourglassIcon, PublicIcon } from '@/icons';
import { useStateStore } from '@/stores';
import type { TaskRead } from '@/api';
import type { Component } from 'vue';
import type { Type } from 'naive-ui/es/button/src/interface';

const state = useStateStore();

const btnTypeMap: Record<string, Type> = {
  done: 'success',
  failed: 'error',
  running: 'info',
};

const iconsMap: Record<string, Component> = {
  done: CheckCircleIcon,
  failed: ErrorIcon,
  running: HourglassIcon,
};

const tasks: TaskRead[] = [
  {
    id: 'foo',
    label: 'Foo Foo Foo Foo Foo Foo Foo Foo Foo Foo ',
    userId: '234f234f',
    status: 'done',
  },
  { id: 'foo', label: 'Foo', userId: '234f234f' },
  { id: 'bar', label: 'Bar', userId: '234f234f', status: 'failed' },
  { id: 'bar', label: 'Bar', userId: '234f234f', status: 'running' },
];
</script>

<template>
  <n-float-button
    id="tasks-widget"
    type="primary"
    menu-trigger="hover"
    :right="42"
    :bottom="state.backtopVisible ? 100 : 42"
  >
    <n-badge :value="9" :offset="[6, -8]">
      <n-icon :component="PublicIcon" />
    </n-badge>
    <template #menu>
      <n-button
        v-for="task in tasks"
        :key="task.id"
        class="task-item"
        :focusable="false"
        :type="btnTypeMap[task.status || 'running']"
        :class="{ done: task.status === 'done', failed: task.status === 'failed' }"
      >
        <template #icon>
          <n-icon :component="iconsMap[task.status || 'running']" />
        </template>
        {{ task.label }}
      </n-button>
    </template>
  </n-float-button>
</template>

<style scoped>
#tasks-widget :deep(.n-float-button__menu) {
  right: 0px;
}

#tasks-widget .task-item {
  box-shadow: var(--fixed-box-shadow);
}

#tasks-widget .task-item.done {
  background-color: var(--col-success);
}

#tasks-widget .task-item.failed {
  background-color: var(--col-error);
}
</style>
