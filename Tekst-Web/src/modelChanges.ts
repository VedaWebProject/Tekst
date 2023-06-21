import { computed, ref, type Ref } from 'vue';

function hashCode(obj: any) {
  const string = String(JSON.stringify(obj));
  let hash = 0;
  for (let i = 0; i < string.length; i++) {
    const code = string.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash;
  }
  return hash;
}

export function useModelChanges(model: Ref<Record<string, any>>) {
  const getPropsHashes = (ofModel: Record<string, any>): Record<string, number> => {
    const hashes: Record<string, number> = {};
    Object.keys(ofModel).forEach((k) => {
      hashes[k] = hashCode(ofModel[k]);
    });
    return hashes;
  };
  const getChanges = (): Record<string, any> => {
    const changes: Record<string, any> = {};
    Object.keys(model.value).forEach((k) => {
      if (modelPropsHashes.value[k] !== hashCode(model.value[k])) {
        changes[k] = model.value[k];
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
