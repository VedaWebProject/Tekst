<script setup lang="ts">
import {
  NButton,
  NFlex,
  NBadge,
  NFloatButton,
  NIcon,
  useDialog,
  type DialogOptions,
} from 'naive-ui';
import { CheckCircleIcon, ErrorIcon, HourglassIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { computed, type Component } from 'vue';
import { useTasks } from '@/composables/tasks';
import { $t, $te } from '@/i18n';

const state = useStateStore();
const { tasks, removeTask } = useTasks();
const dialog = useDialog();

const iconsMap: Record<string, Component> = {
  done: CheckCircleIcon,
  failed: ErrorIcon,
  running: HourglassIcon,
};

const dialogTypeMap: Record<string, DialogOptions['type']> = {
  done: 'success',
  failed: 'error',
  running: 'info',
  waiting: 'default',
};

const hasSuccessfulTasks = computed(() => tasks.value.some((t) => t.status === 'done'));

function handleTaskClick(id: string) {
  const t = tasks.value.find((t) => t.id === id);
  if (!t) return;

  // open dialog if task has failed (to display error info)
  if (t.status === 'failed') {
    const title =
      $t(`tasks.types.${t.type}`) + ' – ' + $t(`tasks.statuses.${t.status || 'running'}`);
    const content = $te(`errors.${t.error}`) ? $t(`errors.${t.error}`) : t.error || '';
    dialog.create({
      type: dialogTypeMap[t.status || 'running'],
      title,
      content,
    });
  }

  // remove if task is done or has failed
  if (t.status === 'done' || t.status === 'failed') {
    removeTask(id);
  }
}
</script>

<template>
  <n-float-button
    v-if="tasks.length > 0"
    id="tasks-widget"
    type="primary"
    menu-trigger="click"
    :right="42"
    :bottom="state.backtopVisible ? 100 : 42"
  >
    <n-badge :value="tasks.length" :offset="[6, -8]">
      <n-icon :component="HourglassIcon" />
    </n-badge>
    <template #menu>
      <div class="task-list">
        <n-flex justify="space-between" align="center" :wrap="false" class="task-list-header">
          <span class="b ellipsis" style="color: var(--base-color)">{{ $t('tasks.title') }}</span>
          <n-button
            v-if="hasSuccessfulTasks"
            quaternary
            circle
            :focusable="false"
            color="var(--base-color)"
            @click="() => removeTask()"
          >
            <template #icon>
              <n-icon :component="CheckCircleIcon" />
            </template>
          </n-button>
        </n-flex>
        <n-flex
          v-for="task in tasks"
          :key="task.id"
          :wrap="false"
          align="center"
          :class="`task-item task-item-${task.status || 'running'}`"
          :focusable="false"
          @click="handleTaskClick(task.id)"
        >
          <n-icon
            class="task-item-icon"
            size="20"
            :component="iconsMap[task.status || 'running']"
          />
          <div class="task-item-label ellipsis">
            {{ $t(`tasks.types.${task.type}`) }}
            ({{ $t(`tasks.statuses.${task.status || 'running'}`) }})
          </div>
        </n-flex>
      </div>
    </template>
  </n-float-button>
</template>

<style scoped>
#tasks-widget :deep(.n-float-button__menu) {
  right: 0px;
  cursor: default;
  padding: 8px 0;
}

#tasks-widget .task-list {
  min-width: 280px;
  max-width: 80vw;
  box-shadow: var(--fixed-box-shadow);
  background-color: var(--base-color);
  border: 2px solid var(--accent-color);
  border-radius: var(--border-radius);
}

#tasks-widget .task-list-header {
  padding: 10px 16px;
  background-color: var(--accent-color);
  margin: 0;
}

#tasks-widget .task-item {
  height: 40px;
  padding: 8px 16px;
  margin: 0px;
  cursor: pointer;
  transition: 0.3s;
  color: var(--text-color);
}

#tasks-widget .task-item:hover {
  background-color: #aaaaaa40;
}

#tasks-widget .task-item.task-item-running {
  font-style: italic;
}

#tasks-widget .task-item.task-item-running:hover {
  cursor: wait;
}

#tasks-widget .task-item > .task-item-icon {
  transition: 0.2s;
}

#tasks-widget .task-item.task-item-running > .task-item-icon {
  color: var(--col-info);
}

#tasks-widget .task-item.task-item-done > .task-item-icon {
  color: var(--col-success);
}

#tasks-widget .task-item.task-item-failed > .task-item-icon {
  color: var(--col-error);
}
</style>
