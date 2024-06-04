import fs from 'node:fs';
import openapiTS from 'openapi-typescript';
import path from 'path';

const SCHEMA_FILE = path.normalize('../Tekst-API/openapi.json');
const TYPES_FILE = path.normalize('src/api/schema.d.ts');

const types = await openapiTS(SCHEMA_FILE, {
  transform(schemaObject) {
    if ('format' in schemaObject && schemaObject.format === 'binary') {
      return schemaObject.nullable ? 'Blob | null' : 'Blob';
    }
  },
});

fs.writeFileSync(TYPES_FILE, types, { encoding: 'utf8' });
