import { marked } from 'marked';
import path from 'path';
import { readdirSync, readFileSync, writeFileSync, rmSync, copyFileSync, existsSync } from 'fs';

const HELP_DIR = path.normalize('translations/help/');
const OUT_DIR = path.normalize('src/assets/help/');
const DOCS_PATH = path.normalize('../docs/generated/help/');
const localeDirs = readdirSync(HELP_DIR, { withFileTypes: true }).filter((entry) =>
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
console.log(`🗑 Deleting old help text translations in ${OUT_DIR} ...`);
for (const d of readdirSync(OUT_DIR, { withFileTypes: true }).filter(
  (entry) => entry.name !== 'README.md' && entry.name !== '.gitignore'
)) {
  rmSync(path.join(d.parentPath, d.name), { recursive: true, force: true });
  //   console.log(`  🗸 ${d.name}/*`);
}
if (existsSync(DOCS_PATH)) {
  console.log(`🗑 Deleting old help text translations in ${DOCS_PATH} ...`);
  for (const d of readdirSync(DOCS_PATH, { withFileTypes: true }).filter(
    (entry) => entry.name !== 'README.md' && entry.name !== '.gitignore'
  )) {
    rmSync(path.join(d.parentPath, d.name), { recursive: true, force: true });
    //   console.log(`  🗸 ${d.name}/*`);
  }
}

// parse current markdown help texts
console.log(`🗘 Processing help text translations in ${HELP_DIR} ...`);
for (const localeDir of localeDirs) {
  const sourceDirPath = path.join(localeDir.parentPath, localeDir.name);
  const mdFiles = readdirSync(sourceDirPath, { withFileTypes: true }).filter(
    (entry) => entry.isFile() && entry.name.endsWith('.md')
  );
  const helpTranslations = {};

  for (const mdFile of mdFiles) {
    const sourceFilePath = path.join(mdFile.parentPath, mdFile.name);
    // copy file to documentation folder
    if (localeDir.name === 'enUS' && existsSync(DOCS_PATH)) {
      copyFileSync(sourceFilePath, path.join(DOCS_PATH, mdFile.name));
    }
    const data = readFileSync(sourceFilePath, 'utf8');
    const title = data.match(/(?<=^#+ ).*$/m)[0]; // ugly, but simple!
    const html = marked.parse(data);
    helpTranslations[mdFile.name.replace(/.md$/, '')] = { title: title, content: html };
    // console.log(`  🗸 ${localeDir.name}/${mdFile.name}`);
  }
  writeFileSync(
    path.join(OUT_DIR, `${localeDir.name}.json`),
    JSON.stringify(helpTranslations, null, 2)
  );
  localeImports.push(`${localeDir.name}: () => import('@/assets/help/${localeDir.name}.json'),`);
}

// generate index.ts
const indexFileContent = `import type {HelpText} from '@/composables/help'; export default {${localeImports.join(
  '\n'
)}} as Record<string, () => Promise<{ default: Record<string, HelpText> }>>;`;

writeFileSync(path.join(OUT_DIR, 'index.ts'), indexFileContent);
