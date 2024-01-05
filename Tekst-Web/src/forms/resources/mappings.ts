import { type Component } from 'vue';
import PlaintextFormItems from '@/forms/resources/PlaintextFormItems.vue';

const resourceUnitFormItems: Record<string, Component> = {
  plaintext: PlaintextFormItems,
};

export default resourceUnitFormItems;
