import { z } from 'zod';
import {
  parse,
  MathNode,
  isOperatorNode,
  isConstantNode,
  isSymbolNode,
  isParenthesisNode,
} from 'mathjs';

const validateNodeRecursively = (node: MathNode, depth: number): void => {
  if (depth > 5) {
    throw new Error('括弧の深さが深すぎます');
  }

  if (isOperatorNode(node)) {
    if (!['+', '-', '*', '/'].includes(node.op))
      throw new Error(`利用できない二項演算子(${node.op})があります`);
    if (node.op === '/' && node.args[1].evaluate({ x: 0 }) === 0) {
      throw new Error('ゼロ除算が検出されました');
    }
    node.args.forEach((arg) => validateNodeRecursively(arg, depth + 1));
  } else if (isConstantNode(node)) {
    if (node.value > 1000000) {
      throw new Error('100万を超える数値が含まれています');
    }
  } else if (isSymbolNode(node)) {
    if (node.name !== 'x') {
      throw new Error('"x" 以外の文字は変数として使えません');
    }
  } else if (isParenthesisNode(node)) {
    validateNodeRecursively(node.content, depth + 1);
  } else {
    throw new Error('不明な文字列が含まれています');
  }
};

const validateExpression = (
  expression: string
): boolean | { message: string } => {
  try {
    const node = parse(expression);
    validateNodeRecursively(node, 0);

    // "x" という名前のSymbolNodeが含まれない場合、バリデーションに失敗する
    if (!node.filter((n) => isSymbolNode(n) && n.name === 'x').length) {
      throw new Error('"x" という変数が含まれていません');
    }
    return true;
  } catch (e) {
    const error = e as Error;
    if (error.name === 'UserError') {
      return { message: error.message };
    }
    return false;
  }
};

export const mathExpressionSchema = z
  .string()
  .max(99, '計算式が100文字以上です')
  .refine(validateExpression, {
    message: '正しい計算式ではありません',
  });
