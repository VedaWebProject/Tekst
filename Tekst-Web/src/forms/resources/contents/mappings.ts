import AudioContentFormItems from '@/forms/resources/contents/AudioContentFormItems.vue';
import ExternalReferencesFormItems from '@/forms/resources/contents/ExternalReferencesFormItems.vue';
import ImagesContentFormItems from '@/forms/resources/contents/ImagesContentFormItems.vue';
import PlainTextContentFormItems from '@/forms/resources/contents/PlainTextContentFormItems.vue';
import RichTextContentFormItems from '@/forms/resources/contents/RichTextContentFormItems.vue';
import TextAnnotationContentFormItems from '@/forms/resources/contents/TextAnnotationContentFormItems.vue';
import { type Component } from 'vue';

const resourceContentFormItems: Record<string, Component> = {
  plainText: PlainTextContentFormItems,
  richText: RichTextContentFormItems,
  textAnnotation: TextAnnotationContentFormItems,
  audio: AudioContentFormItems,
  images: ImagesContentFormItems,
  externalReferences: ExternalReferencesFormItems,
};

export default resourceContentFormItems;
