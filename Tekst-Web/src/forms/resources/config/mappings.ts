import { type Component } from 'vue';
import AnnotationsConfigFormItems from './AnnotationsConfigFormItems.vue';
import ApiCallConfigFormItems from './ApiCallConfigFormItems.vue';
import ContentCssFormItems from './ContentCssFormItems.vue';
import ContentTransformationConfigFormItems from './ContentTransformationConfigFormItems.vue';
import DeepLLinksConfigFormItems from './DeepLLinksConfigFormItems.vue';
import EntriesIntegrationConfigFormItems from './EntriesIntegrationConfigFormItems.vue';
import FocusViewConfigFormItems from './FocusViewConfigFormItems.vue';
import LineLabellingConfigFormItems from './LineLabellingConfigFormItems.vue';
import SearchReplacementsConfigFormItems from './SearchReplacementsConfigFormItems.vue';

export const specialConfigFormItems: Record<string, Component> = {
  focusView: FocusViewConfigFormItems,
  searchReplacements: SearchReplacementsConfigFormItems,
  contentCss: ContentCssFormItems,
  lineLabelling: LineLabellingConfigFormItems,
  deeplLinks: DeepLLinksConfigFormItems,
  annotations: AnnotationsConfigFormItems,
  entriesIntegration: EntriesIntegrationConfigFormItems,
  apiCall: ApiCallConfigFormItems,
  transform: ContentTransformationConfigFormItems,
};
