<template>
  <div class="missing-content i">
    <span class="translucent">{{ $t('contents.noContent') }}</span>
  </div>
</template>

<style scoped>
.missing-content:not(:last-child) {
  padding-left: var(--gap-sm);
  border-left: dotted 3px var(--error-color);
  border-top-left-radius: var(--border-radius);
  border-bottom-left-radius: var(--border-radius);

  padding-bottom: var(--gap-md);
  margin-bottom: var(--gap-md);
  border-bottom: 1px solid var(--primary-color-fade2);
}

.missing-content:last-child {
  margin-bottom: 4px;
}
</style>
