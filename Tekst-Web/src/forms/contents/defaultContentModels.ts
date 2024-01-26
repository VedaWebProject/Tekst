const common = {
  comment: undefined,
  notes: undefined,
};

export const defaultContentModels = {
  plaintext: {
    ...common,
    text: '',
  },
  debug: {
    ...common,
    text: '',
  },
};
