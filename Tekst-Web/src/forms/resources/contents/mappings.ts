import { type Component } from 'vue';
import PlainTextContentFormItems from '@/forms/resources/contents/PlainTextContentFormItems.vue';
import RichTextContentFormItems from '@/forms/resources/contents/RichTextContentFormItems.vue';
import TextAnnotationContentFormItems from '@/forms/resources/contents/TextAnnotationContentFormItems.vue';
import AudioContentFormItems from '@/forms/resources/contents/AudioContentFormItems.vue';

const resourceContentFormItems: Record<string, Component> = {
  plainText: PlainTextContentFormItems,
  richText: RichTextContentFormItems,
  textAnnotation: TextAnnotationContentFormItems,
  audio: AudioContentFormItems,
};

export default resourceContentFormItems;
