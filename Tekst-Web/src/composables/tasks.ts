import { GET, downloadData, type TaskRead } from '@/api';
import { useMessages } from '@/composables/messages';
import { $t, $te } from '@/i18n';
import { useResourcesStore } from '@/stores';
import { useTimeoutPoll } from '@vueuse/core';
import { computed, ref } from 'vue';

const tasks = ref<TaskRead[]>([]);
const { message } = useMessages();

const showTasksWidget = computed(() => tasks.value.length > 0);
const showTasksList = ref(false);

// configure tasks polling
const { resume, pause } = useTimeoutPoll(
  async () => {
    if (!tasks.value.length) {
      pause();
      return;
    }
    const { data, error } = await GET('/platform/tasks/user', {
      headers: {
        'Pickup-Keys': tasks.value.map((t) => t.pickupKey).join(','),
      },
    });
    if (!error) {
      // add new/updated tasks, don't remove any (only happens via user interaction)
      data.forEach(async (task) => {
        const existing = tasks.value.find((et) => et.id === task.id);
        // apply updated/new tasks
        if (!existing) {
          tasks.value.push(task);
        } else if (existing.status !== task.status) {
          // exchange old task object against updated one
          tasks.value = tasks.value.filter((et) => et.id !== task.id);
          tasks.value.push(task);
        }
        // handle updated/new tasks
        if (!existing || existing.status !== task.status) {
          if (task.status === 'done') {
            const result = $te(`tasks.results.${task.type}`)
              ? $t(`tasks.results.${task.type}`, task.result || {})
              : '';
            message.success(
              $t('tasks.successful', { name: $t(`tasks.types.${task.type}`) }) + ' ' + result
            );
            // if this was a resource import, re-load resources data
            if (task.type === 'resource_import') {
              const resources = useResourcesStore();
              resources.load();
            }
          } else if (task.status === 'failed') {
            const detailsText = [
              $te(`errors.${task.error}`) ? $t(`errors.${task.error}`) : null,
              (task.errorDetails || '').trim(),
            ]
              .filter(Boolean)
              .join('\n---\n');
            message.error(
              $t('tasks.failed', { name: $t(`tasks.types.${task.type}`) }),
              detailsText
            );
          }
          // check if task is a completed export task, if so: download
          if (task.type.endsWith('_export') && task.status === 'done') {
            const { data, response, error } = await GET('/platform/tasks/download', {
              params: {
                query: {
                  pickupKey: task.pickupKey,
                },
              },
              parseAs: 'blob',
            });
            if (!error) {
              const filename =
                response.headers.get('content-disposition')?.split('filename=')[1] ||
                task.result?.filename ||
                'export';
              message.info($t('common.downloadSaved', { filename }));
              downloadData(data, filename);
            }
          }
          // check if task is of type 'precompute_data',
          // if so, clear local precomputed cache
          if (task.type === 'precompute_data' && task.status === 'done') {
            const resources = useResourcesStore();
            resources.clearPrecomputedData();
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
  const addTask = (task?: TaskRead) => {
    if (!task) return;
    tasks.value.push(task);
    showTasksList.value = true;
  };
  const removeTask = (id?: string) => {
    if (id) {
      tasks.value = tasks.value.filter((t) => t.id !== id);
    } else {
      tasks.value = tasks.value.filter((t) => t.status !== 'done');
    }
  };

  return {
    tasks,
    addTask,
    removeTask,
    startTasksPolling: resume,
    stopTasksPolling: pause,
    showTasksWidget,
    showTasksList,
  };
}
