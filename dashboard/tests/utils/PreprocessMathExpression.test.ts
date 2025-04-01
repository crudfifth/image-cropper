import { describe, it, expect } from 'vitest';
import { preprocessMathExpression } from '@/utils/PreprocessMathExpression';

describe('スペースが除去される', () => {
  it('', () => {
    const mathExpression = '2 +  3 *　4';
    const preprocessedExpression = preprocessMathExpression(mathExpression);
    expect(preprocessedExpression).toEqual('2+3*4');
  });
});

describe('全角文字が半角文字に変換される', () => {
  it('', () => {
    const mathExpression = '（１＋２）＊３';
    const preprocessedExpression = preprocessMathExpression(mathExpression);
    expect(preprocessedExpression).toEqual('(1+2)*3');
  });
});

describe('ハイフンに似た文字がASCIIのハイフンに変換される', () => {
  it('', () => {
    const mathExpression = '10ｰ9‐8―7─6−5－4ー3一2';
    // 1. 半角長音記号
    // 2. 半角ハイフン(ASCIIのハイフンとは違う文字)
    // 3. ダブルハイフン
    // 4. ボックスドロー文字(ライトハイフン)
    // 5. 全角マイナス
    // 6. 全角ダッシュ
    // 7. 全角ハイフン
    // 8. 漢字の「いち」
    const preprocessedExpression = preprocessMathExpression(mathExpression);
    expect(preprocessedExpression).toEqual('10-9-8-7-6-5-4-3-2');
  });
});

describe('大文字が小文字に変換される', () => {
  it('', () => {
    const mathExpression = 'X+10*2';
    const preprocessedExpression = preprocessMathExpression(mathExpression);
    expect(preprocessedExpression).toEqual('x+10*2');
  });
});
