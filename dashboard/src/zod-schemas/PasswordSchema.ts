import { z } from 'zod';

export const passwordSchema = z
  .string()
  .min(12, { message: 'パスワードは12文字以上にしてください。' })
  .max(16, { message: 'パスワードは16文字以下にしてください。' })
  .regex(/[A-Z]/, {
    message: 'パスワードは英大文字を最低1文字含んでください。',
  })
  .regex(/[a-z]/, {
    message: 'パスワードは英小文字を最低1文字含んでください。',
  })
  .regex(/[0-9]/, { message: 'パスワードは数字を最低1文字含んでください。' })
  .regex(/[@#$%^&*\-+_=[\]{}|\\:'?,/`~"();.]/, {
    message: 'パスワードは記号を最低1文字含んでください.',
  });
