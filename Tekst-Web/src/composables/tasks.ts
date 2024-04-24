import { ref } from 'vue';
import { GET, type TaskRead } from '@/api';
import { useTimeoutPoll } from '@vueuse/core';
import { useMessages } from '@/composables/messages';
import { $t, $te } from '@/i18n';

const tasks = ref<TaskRead[]>([]);
const { message } = useMessages();

// configure tasks polling
const { resume, pause } = useTimeoutPoll(
  async () => {
    const { data, error } = await GET('/platform/tasks');
    if (!error) {
      // add new/updated tasks, don't remove any (only happens via user interaction)
      data.forEach((task) => {
        const existing = tasks.value.find((et) => et.id === task.id);
        // apply updated/new tasks
        if (!existing) {
          tasks.value.push(task);
        } else if (existing.status !== task.status) {
          // exchange old task object against updated one
          tasks.value = tasks.value.filter((et) => et.id !== task.id);
          tasks.value.push(task);
        }
        // pop up message if task is finished
        if (!existing || existing.status !== task.status) {
          if (task.status === 'done') {
            const result = $te(`tasks.results.${task.type}`)
              ? $t(`tasks.results.${task.type}`, task.result || {})
              : '';
            message.success(
              $t('tasks.successful', { name: $t(`tasks.types.${task.type}`) }) + ' ' + result
            );
          } else if (task.status === 'failed') {
            message.error(
              $t('tasks.failed', { name: $t(`tasks.types.${task.type}`) }),
              task.error || undefined
            );
          }
        }
      });
      // stop polling if there are no active tasks
      if (data.filter((t) => ['running', 'waiting'].includes(t.status || '')).length === 0) {
        pause();
      }
      // sort by start time
      tasks.value.sort(
        (a, b) =>
          (b.startTime ? Date.parse(b.startTime) : 0) - (a.startTime ? Date.parse(a.startTime) : 0)
      );
    }
  },
  5000,
  { immediate: false }
);

export function useTasks() {
  const remove = (id: string) => {
    tasks.value = tasks.value.filter((t) => t.id !== id);
  };

  return { tasks, remove, start: resume, stop: pause };
}
