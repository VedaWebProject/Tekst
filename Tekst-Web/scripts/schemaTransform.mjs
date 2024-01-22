import fs from 'node:fs';
import openapiTS from 'openapi-typescript';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import path from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCHEMA_FILE = path.normalize(`${__dirname}/../../Tekst-API/openapi.json`);
const TYPES_FILE = path.normalize(`${__dirname}/../src/api/schema.d.ts`);

const types = await openapiTS(SCHEMA_FILE, {
  transform(schemaObject) {
    if ('format' in schemaObject && schemaObject.format === 'binary') {
      return schemaObject.nullable ? 'Blob | null' : 'Blob';
    }
  },
});

fs.writeFileSync(TYPES_FILE, types, { encoding: 'utf8' });
