import { describe, it, expect } from 'vitest';
import { getLastMonday } from '@/utils/Utils';

describe('getLastMonday', () => {
  it('日付が金曜日の場合、その前の月曜日を取得できる', () => {
    const date = new Date('2021-10-01'); // 金曜日
    const result = getLastMonday(date);
    expect(result).toEqual(new Date('2021-09-27T00:00:00'));
  });
  it('日付が土曜日の場合、その前の月曜日を取得できる', () => {
    const date = new Date('2021-10-02'); // 土曜日
    const result = getLastMonday(date);
    expect(result).toEqual(new Date('2021-09-27T00:00:00'));
  });
  it('日付が日曜日の場合、その前の月曜日を取得できる', () => {
    const date = new Date('2021-10-03'); // 日曜日
    const result = getLastMonday(date);
    expect(result).toEqual(new Date('2021-09-27T00:00:00'));
  });
  it('月曜日の場合は当日を取得できる', () => {
    const date = new Date('2021-10-04'); // 月曜日
    const result = getLastMonday(date);
    expect(result).toEqual(new Date('2021-10-04T00:00:00'));
  });
});
