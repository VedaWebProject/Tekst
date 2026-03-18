<template>
  <div class="missing-content i">
    <span class="translucent">[{{ $t('contents.noContent') }}]</span>
  </div>
</template>

<style scoped>
.missing-content:not(:last-child) {
  padding-bottom: var(--gap-md);
  margin-bottom: var(--gap-md);
  border-bottom: 1px solid var(--primary-color-fade2);
}

.missing-content:last-child {
  margin-bottom: 4px;
}
</style>
