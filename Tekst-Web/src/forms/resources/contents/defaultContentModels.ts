const common = {
  comment: undefined,
  notes: undefined,
};

export const defaultContentModels = {
  plainText: {
    ...common,
    text: '',
  },
  richText: {
    ...common,
    html: '',
  },
  textAnnotation: {
    ...common,
    tokens: [
      {
        token: undefined,
        annotations: [],
      },
    ],
  },
  locationMetadata: {
    ...common,
    entries: [
      {
        key: undefined,
        value: undefined,
      },
    ],
  },
  audio: {
    ...common,
    files: [
      {
        url: undefined,
        caption: undefined,
      },
    ],
  },
  images: {
    ...common,
    files: [
      {
        url: '',
        thumbUrl: undefined,
        sourceUrl: undefined,
        caption: undefined,
      },
    ],
  },
  externalReferences: {
    ...common,
    links: [
      {
        url: undefined,
        title: undefined,
        description: undefined,
      },
    ],
  },
  apiCall: {
    ...common,
    url: undefined,
  },
};
