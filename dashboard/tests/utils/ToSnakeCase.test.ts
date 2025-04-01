import { describe, it, expect } from 'vitest';
import { toSnakeCase } from '@/utils/ToSnakeCase';

describe('objectPropertyNameToSnakeCase', () => {
  it('オブジェクトのキーがスネークケースに変換される(シンプルなオブジェクト)', () => {
    const obj = {
      camelCaseKey: 'value',
    };
    const result = toSnakeCase(obj);
    expect(result).toEqual({
      camel_case_key: 'value',
    });
  });
  it('オブジェクトのキーがスネークケースに変換される(ネストしたオブジェクト)', () => {
    const obj = {
      camelCaseKey: 'value',
      nestedObject: {
        nestedCamelCaseKey: 'nestedValue',
      },
    };
    const result = toSnakeCase(obj);
    expect(result).toEqual({
      camel_case_key: 'value',
      nested_object: {
        nested_camel_case_key: 'nestedValue',
      },
    });
  });
  it('オブジェクトのキーがスネークケースに変換される(ネストしたオブジェクトの配列)', () => {
    const obj = {
      camelCaseKey: 'value',
      nestedObjectArray: [
        {
          nestedCamelCaseKey: 'nestedValue',
        },
      ],
    };
    const result = toSnakeCase(obj);
    expect(result).toEqual({
      camel_case_key: 'value',
      nested_object_array: [
        {
          nested_camel_case_key: 'nestedValue',
        },
      ],
    });
  });
  it('オブジェクトのキーがスネークケースに変換される(複雑なオブジェクト)', () => {
    const obj = {
      camelCaseKey: 'value',
      nestedObject: {
        nestedCamelCaseKey: 'nestedValue',
        deeplyNestedObject: { deeplyNestedCamelCaseKey: 'deeplyNestedValue' },
      },
      nestedObjectArray: [
        { nestedCamelCaseKey: 'nestedValue' },
        { nestedCamelCaseKey: 'nestedValue2' },
      ],
    };
    const result = toSnakeCase(obj);
    expect(result).toEqual({
      camel_case_key: 'value',
      nested_object: {
        nested_camel_case_key: 'nestedValue',
        deeply_nested_object: {
          deeply_nested_camel_case_key: 'deeplyNestedValue',
        },
      },
      nested_object_array: [
        { nested_camel_case_key: 'nestedValue' },
        { nested_camel_case_key: 'nestedValue2' },
      ],
    });
  });
});
