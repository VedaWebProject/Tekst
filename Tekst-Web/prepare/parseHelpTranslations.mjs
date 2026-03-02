import { readdirSync, readFileSync, rmSync, writeFileSync } from 'fs';
import { marked } from 'marked';
import path from 'path';
import jsdom from 'jsdom';

const SOURCE_DIR = path.normalize('i18n/help/');
const TARGET_DIR = path.normalize('src/assets/i18n/help/');

function addTOC(html) {
  if (!html) return '';
  const { document } = new jsdom.JSDOM(html).window;
  const ul = document.createElement('ul');
  ul.style.padding = '0px';
  ul.style.marginTop = '0.25rem';
  const headings = document.querySelectorAll('h2,h3,h4,h5,h6');
  if (headings.length <= 2) return document.body.innerHTML;
  headings.forEach((h) => {
    const hSlug = 'helptext-' + h.innerHTML.replace(/\W+/g, '-').toLowerCase();
    h.setAttribute('id', hSlug);
    const level = Number.parseInt(h.tagName.charAt(1));
    const li = document.createElement('li');
    li.style.paddingLeft = `${level - 1}rem`;
    li.style.fontSize = `${14 + 8 / level}px`;
    li.style.listStylePosition = 'inside';
    const a = document.createElement('a');
    a.innerHTML = h.innerHTML.toString();
    a.setAttribute('href', `#${hSlug}`);
    li.appendChild(a);
    ul.appendChild(li);
  });
  const mainHeading = document.getElementsByTagName('h1')[0];
  // insert TOC into document
  if (mainHeading) {
    mainHeading.after(ul);
  } else {
    document.prepend(ul);
  }
  return document.body.innerHTML;
}

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
    const title = data.match(/(?<=^#+ ).*$/m)[0]?.replace(/\\\*/, '*'); // ugly, but efficient!
    const content = addTOC(marked.parse(data));
    const helpKey = mdFile.name.split('.')[0];
    const scope = mdFile.name.split('.').length === 3 ? mdFile.name.split('.')[1] : 'v';
    helpTranslations[helpKey] = { title, content, scope };
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
