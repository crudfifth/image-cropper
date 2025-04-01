import { TimePeriodType } from '@/types';

export const createTimeSeriesDataLabels = (input: {
  timePeriod: TimePeriodType;
  startDate: Date | undefined; // four-hourの時にだけ使う
}): string[] => {
  switch (input.timePeriod) {
    case 'four-hour': {
      const ret = Array(240)
        .fill(0)
        .map((_, index) => {
          if (input.startDate === undefined) {
            throw new Error('startDateが不正です');
          }
          const date = new Date(input.startDate.getTime() + index * 60000);
          const minutes = date.getMinutes();
          const hours = date.getHours();
          if (minutes % 15 === 0) {
            const formattedHours = hours < 10 ? `0${hours}` : `${hours}`;
            const formattedMinutes =
              minutes < 10 ? `0${minutes}` : `${minutes}`;
            return `${formattedHours}:${formattedMinutes}`;
          } else {
            return '';
          }
        });

      return ret;
    }
    case 'day': {
      return Array(48)
        .fill(0)
        .map((_, index) => {
          const hour = Math.floor(index / 2);
          return index % 2 === 0 ? `${hour.toString().padStart(2, '0')}` : '';
        });
    }
    case 'week': {
      return '月,火,水,木,金,土,日'.split(',');
    }
    case 'month': {
      return Array(31)
        .fill(0)
        .map((_, index) => `${index + 1}`);
    }
    // case 'year': {
    //   return Array(12)
    //     .fill(0)
    //     .map((_, index) => `${index + 1}`);
    // }
    default: {
      return [];
    }
  }
};

export const createTimeSeriesChartValues = (input: {
  data: any[];
  valueSelector: (item: any) => number;
  timePeriod: TimePeriodType;
}): number[] => {
  switch (input.timePeriod) {
    case 'day': {
      const values = Array(48).fill(0);
      input.data.forEach((item) => {
        const index = item.hour * 2 + Math.floor(item.minute / 30);
        values[index] += input.valueSelector(item);
      });
      return values;
    }
    case 'week': {
      const values = Array(7).fill(0);
      input.data.forEach((item) => {
        const date = new Date(item.year, item.month - 1, item.date);
        const dayOfWeek = date.getDay();
        const dayIndex = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // 日曜日が0のインデックス→月曜日が0のインデックスに変換
        values[dayIndex] = input.valueSelector(item);
      });
      return values;
    }
    case 'month': {
      const values = Array(31).fill(0);
      input.data.forEach((item) => {
        values[item.date - 1] = input.valueSelector(item);
      });
      return values;
    }
    case 'year': {
      const values = Array(12).fill(0);
      input.data.forEach((item) => {
        values[item.month - 1] = input.valueSelector(item);
      });
      return values;
    }
    default: {
      const values = Array(12).fill(0);
      return values;
    }
  }
};
