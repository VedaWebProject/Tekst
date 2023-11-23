import { marked } from 'marked';
import DOMPurify from 'isomorphic-dompurify';
import path from 'path';
import { readdirSync, readFileSync, writeFileSync, rmSync, copyFileSync } from 'fs';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HELP_DIR = path.normalize(`${__dirname}/../translations/help/`);
const OUT_DIR = path.normalize(`${__dirname}/../src/assets/help/`);
const DOCS_PATH = path.normalize(`${__dirname}/../../docs/generated/help/`);
const localeDirs = readdirSync(HELP_DIR, { withFileTypes: true }).filter((entry) =>
  entry.isDirectory()
);

const localeImports = []; // fot imports in index file

// delete old target files
console.log(`🗑 Deleting old help text translations in ${OUT_DIR} ...`);
for (const d of readdirSync(OUT_DIR, { withFileTypes: true }).filter(
  (entry) => entry.name !== 'README.md' && entry.name !== '.gitignore'
)) {
  rmSync(path.join(d.path, d.name), { recursive: true, force: true });
  //   console.log(`  🗸 ${d.name}/*`);
}
console.log(`🗑 Deleting old help text translations in ${DOCS_PATH} ...`);
for (const d of readdirSync(DOCS_PATH, { withFileTypes: true }).filter(
  (entry) => entry.name !== 'README.md' && entry.name !== '.gitignore'
)) {
  rmSync(path.join(d.path, d.name), { recursive: true, force: true });
  //   console.log(`  🗸 ${d.name}/*`);
}

// parse current markdown help texts
console.log(`🗘 Processing help text translations in ${HELP_DIR} ...`);
for (const localeDir of localeDirs) {
  const sourceDirPath = path.join(localeDir.path, localeDir.name);
  const mdFiles = readdirSync(sourceDirPath, { withFileTypes: true }).filter(
    (entry) => entry.isFile() && entry.name.endsWith('.md')
  );
  const helpTranslations = {};

  for (const mdFile of mdFiles) {
    const sourceFilePath = path.join(mdFile.path, mdFile.name);
    // copy file to documentation folder
    if (localeDir.name === 'enUS') {
      copyFileSync(sourceFilePath, path.join(DOCS_PATH, mdFile.name));
    }
    const data = readFileSync(sourceFilePath, 'utf8');
    const title = data.match(/(?<=^# ).*$/m)[0]; // ugly, but simple!
    const html = DOMPurify.sanitize(marked.parse(data));
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
const indexFileContent = `import type {HelpText} from '@/help'; export default {${localeImports.join(
  '\n'
)}} as Record<string, () => Promise<{ default: Record<string, HelpText> }>>;`;

writeFileSync(path.join(OUT_DIR, 'index.ts'), indexFileContent);
