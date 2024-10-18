import { computed, ref, type Ref } from 'vue';

function hashCode(obj: unknown) {
  const string = String(JSON.stringify(obj));
  let hash = 0;
  for (let i = 0; i < string.length; i++) {
    const code = string.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash;
  }
  return hash;
}

export function useModelChanges(model: Ref<Record<string, unknown> | undefined>) {
  const getPropsHashes = (ofModel: Record<string, unknown> | undefined): Record<string, number> => {
    const hashes: Record<string, number> = {};
    if (!ofModel) return hashes;
    Object.keys(ofModel).forEach((k) => {
      hashes[k] = hashCode(ofModel[k]);
    });
    return hashes;
  };
  const getChanges = (forceProps?: string[]): Record<string, unknown> => {
    const changes: Record<string, unknown> = {};
    if (!model.value) return changes;
    Object.keys(model.value).forEach((k) => {
      if (modelPropsHashes.value[k] !== hashCode(model.value?.[k]) || forceProps?.includes(k)) {
        changes[k] = model.value?.[k];
      }
    });
    return changes;
  };

  const modelHash = ref(hashCode(model.value));
  const modelPropsHashes = ref(getPropsHashes(model.value));
  const changed = computed(() => modelHash.value !== hashCode(model.value));
  const reset = () => {
    modelHash.value = hashCode(model.value);
    modelPropsHashes.value = getPropsHashes(model.value);
  };

  return {
    changed,
    getChanges,
    reset,
  };
}
