import { readdirSync, readFileSync, rmSync, writeFileSync } from 'fs';
import { marked } from 'marked';
import path from 'path';

const SOURCE_DIR = path.normalize('i18n/help/');
const TARGET_DIR = path.normalize('src/assets/i18n/help/');

const localeDirs = readdirSync(SOURCE_DIR, { withFileTypes: true }).filter((entry) =>
  entry.isDirectory()
);

const localeImports = []; // imports in index file

// customize marked's link renderer to include "target" and "rel" attributes
const renderer = {
  link(href, title, text) {
    const link = marked.Renderer.prototype.link.call(this, href, title, text);
    const titleAttr = title ? ` title="${title}"` : '';
    return link.replace('<a', `<a target="_blank" rel="noreferrer"${titleAttr} `);
  },
};
marked.use({ renderer });

// delete old target files
console.log(`🗑 Deleting old help text translations in ${TARGET_DIR} ...`);
for (const d of readdirSync(TARGET_DIR, { withFileTypes: true }).filter(
  (entry) => entry.name !== 'README.md' && entry.name !== '.gitignore'
)) {
  rmSync(path.join(d.parentPath, d.name), { recursive: true, force: true });
}

// parse current markdown help texts
console.log(`🗘 Processing help text translations in ${SOURCE_DIR} ...`);
for (const localeDir of localeDirs) {
  const sourceDirPath = path.join(localeDir.parentPath, localeDir.name);
  const mdFiles = readdirSync(sourceDirPath, { withFileTypes: true }).filter(
    (entry) => entry.isFile() && entry.name.endsWith('.md')
  );
  const helpTranslations = {};

  for (const mdFile of mdFiles) {
    const sourceFilePath = path.join(mdFile.parentPath, mdFile.name);
    const data = readFileSync(sourceFilePath, 'utf8');
    const title = data.match(/(?<=^#+ ).*$/m)[0]; // ugly, but simple!
    const html = marked.parse(data);
    helpTranslations[mdFile.name.replace(/.md$/, '')] = { title: title, content: html };
  }
  writeFileSync(path.join(TARGET_DIR, `${localeDir.name}.json`), JSON.stringify(helpTranslations));
  localeImports.push(
    `${localeDir.name}: () => import('@/assets/i18n/help/${localeDir.name}.json'),`
  );
}

// generate index.ts
const indexFileContent = `import type {HelpText} from '@/composables/help'; export default {${localeImports.join(
  '\n'
)}} as Record<string, () => Promise<{ default: Record<string, HelpText> }>>;`;

writeFileSync(path.join(TARGET_DIR, 'index.ts'), indexFileContent);
