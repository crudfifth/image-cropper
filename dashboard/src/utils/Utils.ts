import resolveConfig from 'tailwindcss/resolveConfig';

export const tailwindConfig = () => {
  // Tailwind config
  return resolveConfig('./src/css/tailwind.config.js' as any);
};

export const hexToRGB = (h: any) => {
  let r = '';
  let g = '';
  let b = '';
  if (h.length === 4) {
    r = `0x${h[1]}${h[1]}`;
    g = `0x${h[2]}${h[2]}`;
    b = `0x${h[3]}${h[3]}`;
  } else if (h.length === 7) {
    r = `0x${h[1]}${h[2]}`;
    g = `0x${h[3]}${h[4]}`;
    b = `0x${h[5]}${h[6]}`;
  }
  return `${+r},${+g},${+b}`;
};

export const formatValue = (value: any) =>
  Intl.NumberFormat('ja-JP', {
    style: 'currency',
    currency: 'JPY',
    maximumSignificantDigits: 3,
    // notation: 'compact',
  }).format(value);

export const formatThousands = (value: any) =>
  Intl.NumberFormat('ja-JP', {
    maximumSignificantDigits: 3,
    notation: 'compact',
  }).format(value);

export const formatDate = (date: Date) => {
  const d = new Date(date);
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`;
};

// 月の初日から何週目かを取得
export const getWeekIndexOfMonth = (targetDate: Date) => {
  // 月の初日の日付オブジェクトを取得
  const firstDayOfMonth = new Date(
    targetDate.getFullYear(),
    targetDate.getMonth(),
    1
  );

  // 月の初日の曜日を取得 (0 (日曜) ~ 6 (土曜))
  let dayOfWeek = firstDayOfMonth.getDay();

  // 月曜開始として判定するために日曜を7として扱う
  dayOfWeek = dayOfWeek === 0 ? 7 : dayOfWeek;

  // その月の何週目かを計算(0始まり)
  const weekIndexOfMonth =
    Math.ceil((targetDate.getDate() + dayOfWeek - 1) / 7) - 1;
  return weekIndexOfMonth;
};

// その日に最近の最後の月曜日を取得
export const getLastMonday = (date: Date) => {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1); // 日曜日だった場合に調整
  const ret = new Date(d.setDate(diff));
  ret.setHours(0, 0, 0, 0);
  return ret;
};

// 当月の1日を取得
export const getFirstDayOfMonth = (date: Date) => {
  return new Date(date.getFullYear(), date.getMonth(), 1, 0, 0, 0, 0);
};

// 今日の0時を取得
export const getZeroOClock = (date: Date) => {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
};

export const getLast30Minutes = (date: Date) => {
  const d = new Date(date);
  if (d.getMinutes() < 30) {
    d.setMinutes(0);
  } else {
    d.setMinutes(30);
  }
  return d;
};

export const getLast2Hour = (date: Date) => {
  const d = new Date(date);
  d.setHours(d.getHours() - 2);
  return d;
};
