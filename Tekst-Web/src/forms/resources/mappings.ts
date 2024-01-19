import { type Component } from 'vue';
import PlaintextFormItems from '@/forms/resources/PlaintextFormItems.vue';

const resourceContentFormItems: Record<string, Component> = {
  plaintext: PlaintextFormItems,
};

export default resourceContentFormItems;
