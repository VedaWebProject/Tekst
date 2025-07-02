<script setup lang="ts">
import { useTasks } from '@/composables/tasks';
import { $t, $te } from '@/i18n';
import { CheckCircleIcon, ErrorIcon, HourglassIcon } from '@/icons';
import { useStateStore } from '@/stores';
import {
  NBadge,
  NButton,
  NFlex,
  NFloatButton,
  NIcon,
  NScrollbar,
  useDialog,
  type DialogOptions,
} from 'naive-ui';
import { computed, type Component } from 'vue';

const state = useStateStore();
const { tasks, removeTask, showTasksList } = useTasks();
const dialog = useDialog();

const statusThemes: Record<
  string,
  { icon: Component; color: string; dialogType: DialogOptions['type'] }
> = {
  done: { icon: CheckCircleIcon, color: 'var(--success-color)', dialogType: 'success' },
  failed: { icon: ErrorIcon, color: 'var(--error-color)', dialogType: 'error' },
  running: { icon: HourglassIcon, color: 'var(--info-color)', dialogType: 'info' },
  waiting: { icon: HourglassIcon, color: 'var(--info-color)', dialogType: 'default' },
};

const hasSuccessfulTasks = computed(() => tasks.value.some((t) => t.status === 'done'));

function handleTaskClick(id: string) {
  const t = tasks.value.find((t) => t.id === id);
  if (!t) return;

  // open dialog if task has failed (to display error info)
  if (t.status === 'failed') {
    const errorDetails = [
      $te(`errors.${t.error}`) ? $t(`errors.${t.error}`) : t.error || null,
      (t.errorDetails || '').trim(),
    ]
      .filter(Boolean)
      .join('\n---\n');
    dialog.create({
      type: statusThemes[t.status].dialogType,
      title: $t(`tasks.types.${t.type}`) + ' – ' + $t(`tasks.statuses.${t.status}`),
      content: errorDetails,
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
    id="tasks-widget"
    v-model:show-menu="showTasksList"
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
        <n-scrollbar style="max-height: 60vh">
          <n-flex
            v-for="task in tasks"
            :key="task.id"
            :wrap="false"
            align="center"
            :class="`task-item task-item-${task.status}`"
            :focusable="false"
            @click="handleTaskClick(task.id)"
          >
            <n-icon
              class="task-item-icon text-medium"
              :component="statusThemes[task.status].icon"
              :color="statusThemes[task.status].color"
            />
            <div class="text-medium ellipsis">
              {{ $t(`tasks.types.${task.type}`) }}
              ({{ $t(`tasks.statuses.${task.status}`) }})
            </div>
          </n-flex>
        </n-scrollbar>
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
  box-shadow: var(--affix-box-shadow);
  background-color: var(--base-color);
  border: 2px solid var(--primary-color);
  border-radius: var(--border-radius);
}

#tasks-widget .task-list-header {
  padding: 10px 16px;
  background-color: var(--primary-color);
  margin: 0;
}

#tasks-widget .task-item {
  height: 40px;
  padding: 8px 16px;
  margin: 0px;
  cursor: pointer;
  transition: 0.2s;
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
</style>
