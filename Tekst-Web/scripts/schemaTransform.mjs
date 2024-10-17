import fs from 'node:fs';
import openapiTS, { astToString, transformSchemaObject } from 'openapi-typescript';
import path from 'path';
import ts from 'typescript';
import crypto from 'crypto';

const SCHEMA_FILE_URL = new URL(path.normalize('../../Tekst-API/openapi.json'), import.meta.url);
const TYPES_FILE = path.normalize('src/api/schema.d.ts');

const BLOB = ts.factory.createTypeReferenceNode(ts.factory.createIdentifier('Blob'));
const NULL = ts.factory.createLiteralTypeNode(ts.factory.createNull());

const processedSchemaObjectHashes = new Set();

console.log(
  'Transforming OpenAPI schema to TypeScript types from file:',
  SCHEMA_FILE_URL.href,
  '...'
);

function hashSchemaObject(schemaObject, options) {
  return crypto
    .createHash('md5')
    .update(JSON.stringify(schemaObject) + JSON.stringify(options))
    .digest('hex');
}

const ast = await openapiTS(SCHEMA_FILE_URL, {
  transform(schemaObject, options) {
    const hash = hashSchemaObject(schemaObject, options);
    // remove null type properties of update models that have been forced to be nullable
    if (schemaObject.optionalNullable !== undefined && !processedSchemaObjectHashes.has(hash)) {
      // remove "null" from union types (if present)
      if (schemaObject.anyOf && schemaObject.optionalNullable === false) {
        schemaObject.anyOf = schemaObject.anyOf.filter((t) => t.type !== 'null');
      }
      processedSchemaObjectHashes.add(hash);
      return {
        schema: transformSchemaObject(schemaObject, options),
        questionToken: true, // set field to optional
      };
    }
    // handle binary types as `Blob` or `Blob | null`
    if (schemaObject.format === 'binary') {
      return schemaObject.nullable ? ts.factory.createUnionTypeNode([BLOB, NULL]) : BLOB;
    }
  },
});

console.log('Writing schema types to file:', TYPES_FILE, '...');
fs.writeFileSync(TYPES_FILE, astToString(ast), { encoding: 'utf8' });
