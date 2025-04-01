import { describe, it, expect } from 'vitest';
import { mathExpressionSchema } from '@/zod-schemas/MathExpressionSchema';

describe('mathExpressionSchema', () => {
  const correctExpressions = [
    'x+1',
    'x-1',
    'x*1',
    'x/1',
    'x+1+1',
    'x-1-1',
    'x*1*1',
    'x/1/1',
    'x+(1+1)',
    'x-(1-1)',
    'x*(1*1)',
    'x+(1*1)',
    'x-(1/1)',
    'x*(1+1)',
    'x*200',
    '(x)*200',
    'x+1.23',
    '-5+x',
  ];
  correctExpressions.forEach((expression) => {
    it(`正しい式(${expression})に対してバリデーションが成功する`, () => {
      const result = mathExpressionSchema.safeParse(expression);
      expect(result.success).toBe(true);
    });
  });

  const incorrectExpressions = [
    '1+1',
    'x+y+1',
    'x+1+',
    'x+1 1',
    'x+1/0',
    '((((((x+1))))))',
    'x+' + '1+'.repeat(49) + '1',
    'x+1000001',
  ];
  incorrectExpressions.forEach((expression) => {
    it(`不正な式(${expression})に対してバリデーションが失敗する`, () => {
      const result = mathExpressionSchema.safeParse(expression);
      expect(result.success).toBe(false);
    });
  });
});
