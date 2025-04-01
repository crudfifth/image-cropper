const toSnakeCaseString = (str: string): string =>
  str.replace(/([A-Z])/g, '_$1').toLowerCase();

// オブジェクトのプロパティ名をキャメルケース→スネークケースに変換する
// パスカルケースのプロパティが紛れ込んでいるとうまく動作しないので注意
// 例: { userName: 'hoge', userAge: 20 } => { user_name: 'hoge', user_age: 20 }
export const toSnakeCase = <T extends Record<string, any>>(obj: T): T =>
  Object.entries(obj).reduce(
    (acc, [key, value]) => ({
      ...acc,
      [toSnakeCaseString(key)]: Array.isArray(value)
        ? value.map((val) =>
            typeof val === 'object' && val !== null ? toSnakeCase(val) : val
          )
        : typeof value === 'object' && value !== null
        ? toSnakeCase(value)
        : value,
    }),
    {} as T
  );
