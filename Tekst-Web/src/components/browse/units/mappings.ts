import { defineAsyncComponent, type Component } from 'vue';

const unitComponents: Record<string, Component> = {
  plaintext: defineAsyncComponent(() => import('@/components/browse/units/PlaintextUnit.vue')),
};

export default unitComponents;
