import fs from 'fs';
import path from 'path';
import YAML from 'yaml';

const SOURCE_DIR = path.normalize('i18n/ui/');
const TARGET_DIR = path.normalize('src/assets/i18n/ui/');

const translationYamlFiles = fs
  .readdirSync(SOURCE_DIR, { withFileTypes: true })
  .filter(
    (entry) => entry.isFile() && (entry.name.endsWith('.yaml') || entry.name.endsWith('.yml'))
  );

// delete old target files
console.log(`🗑 Deleting old UI translations in ${TARGET_DIR} ...`);
for (const d of fs
  .readdirSync(TARGET_DIR, { withFileTypes: true })
  .filter((entry) => entry.name !== 'README.md' && entry.name !== '.gitignore')) {
  fs.rmSync(path.join(d.parentPath, d.name), { recursive: true, force: true });
}

// parse current UI translations
console.log(`🗘 Processing UI translations in ${SOURCE_DIR} ...`);
for (const translationYamlFile of translationYamlFiles) {
  const localeKey = translationYamlFile.name.split('.').slice(0, -1).join('.');
  const sourceFileExt = translationYamlFile.name.split('.').pop();
  fs.writeFileSync(
    path.join(TARGET_DIR, `${localeKey}.json`),
    JSON.stringify(
      YAML.parse(fs.readFileSync(path.join(SOURCE_DIR, `${localeKey}.${sourceFileExt}`), 'utf8'))
    )
  );
}
