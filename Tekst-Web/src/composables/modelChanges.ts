import { $t } from '@/i18n';
import { useDialog } from 'naive-ui';
import { computed, ref, type Ref } from 'vue';
import { onBeforeRouteLeave } from 'vue-router';

export function useModelChanges(model: Ref<Record<string, unknown> | undefined>) {
  const dialog = useDialog();
  const valuesToJSON = (o: Record<string, unknown> | undefined) =>
    Object.fromEntries(Object.entries(o || {}).map(([k, v]) => [k, JSON.stringify(v)]));
  const beforeEntriesJson = ref(valuesToJSON(model.value));
  const afterEntriesJson = computed(() => valuesToJSON(model.value));
  const changed = computed(() =>
    Object.entries(afterEntriesJson.value).some(([k, v]) => v !== beforeEntriesJson.value[k])
  );

  // register router guard to prevent navigation if there are unsaved changes
  onBeforeRouteLeave(
    async (_to, _from) =>
      !changed.value ||
      (await new Promise((resolve) =>
        dialog.warning({
          title: $t('common.warning'),
          content: $t('common.dirtyFormConfirm'),
          positiveText: $t('common.yes'),
          negativeText: $t('common.no'),
          onPositiveClick: () => resolve(true),
          onNegativeClick: () => resolve(false),
          onClose: () => resolve(false),
          onEsc: () => resolve(false),
          onMaskClick: () => resolve(false),
        })
      ))
  );

  function getChanges(forceProps?: string[]) {
    if (!changed.value) {
      return {};
    } else {
      return Object.fromEntries(
        Object.entries(afterEntriesJson.value)
          .filter(([k, v]) => v !== beforeEntriesJson.value[k] || forceProps?.includes(k))
          .map(([k, v]) => [k, JSON.parse(v)])
      );
    }
  }

  function reset() {
    beforeEntriesJson.value = valuesToJSON(model.value);
  }

  return {
    changed,
    getChanges,
    reset,
  };
}
