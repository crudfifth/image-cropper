export const preprocessMathExpression = (expression: string): string =>
  expression
    // 全角の文字を半角文字に変換
    .replace(/[Ａ-Ｚａ-ｚ０-９（）＋／＊]/g, (char) =>
      String.fromCharCode(char.charCodeAt(0) - 0xfee0)
    )
    // ハイフンに似た文字をASCIIのハイフンに変換 (日本語環境での誤入力が多いので)
    .replace(/[-˗ᅳ᭸‐‑‒–—―⁃⁻−▬─━➖ーㅡ﹘﹣－ｰ𐄐𐆑一]/gu, '-')
    // スペースを除去
    .replace(/[\s　]/g, '') // eslint-disable-line no-irregular-whitespace
    // 大文字を小文字に変換
    .toLowerCase();
