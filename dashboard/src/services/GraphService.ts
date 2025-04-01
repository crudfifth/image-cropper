import { z } from 'zod';
import { mapValues } from 'lodash-es';
import GraphAdaptersRepository from '@/repositories/GraphAdaptersRepository';
import UserRepository from '@/repositories/UserRepository';
import GraphDataRepository from '@/repositories/GraphDataRepository';
import {
  graphKeySchema,
  graphDataSchema,
} from '@/repositories/GraphDataRepository';
import type { TimePeriodType } from '@/types';
import type { InputType as RepositoryInputType } from '@/repositories/GraphDataRepository';
import type { ResponseType as RepositoryResponseType } from '@/repositories/GraphDataRepository';

import MockAdapter from 'axios-mock-adapter';
import axios from 'axios';

export type InputType = Omit<RepositoryInputType, 'companyId'> & {
  timePeriodType: TimePeriodType;
};

const responseSchema = z.record(
  graphKeySchema,
  z.object({
    isEnabled: z.boolean(),
    name: z.string(),
    dataPoints: graphDataSchema.array(),
  })
);

export type GraphKeyType = z.infer<typeof graphKeySchema>;
// export type ResponseType = z.infer<typeof responseSchema>;
export type ResponseType = {
  [key: string]: {
    isEnabled: boolean;
    name: string;
    dataPoints: DataPointType[];
  };
};

export type DataPointType = z.infer<typeof graphDataSchema>;

//
const isMockEnabled = import.meta.env.VITE_API_MOCK === 'true';

if (isMockEnabled) {
  const mock = new MockAdapter(axios);
  import('@/mocks/graphDataMocks').then((module) => {
    mock.onGet("/api/graph-data").reply(200, module.default);
  });
}
//

const fetchDataPoints = async (input: InputType) => {
  const selectedCompanyId = await UserRepository.getSelectedCompanyId();
  let data: RepositoryResponseType = {};

  switch (input.timePeriodType) {
    case 'day':
      data = await GraphDataRepository.fetchGraphHoursData({
        ...input,
        companyId: selectedCompanyId,
      });
      break;
    case 'week':
      data = await GraphDataRepository.fetchGraphDatesData({
        ...input,
        companyId: selectedCompanyId,
      });
      break;
    case 'month':
      data = await GraphDataRepository.fetchGraphDatesData({
        ...input,
        week: undefined,
        date: undefined,
        companyId: selectedCompanyId,
      });
      break;
    case 'four-hour':
      data = await GraphDataRepository.fetchGraphMinutesData({
        ...input,
        companyId: selectedCompanyId,
      });
      break;
    case 'year':
      throw new Error('Not implemented');
    default:
      const unreachable: never = input.timePeriodType; // eslint-disable-line
  }

  if (Object.keys(data).length === 0) {
    return {
      '1': [],
      '2': [],
      '3': [],
      '4': [],
      '5': [],
      '6': [],
      '7': [],
      '8': [],
      '9': [],
      '10': [],
      '11': [],
      '12': [],
      '13': [],
      '14': [],
      '15': [],
      '16': [],
    };
  }

  return data;
};

export default {
  // TODO: 廃止予定
  async fetchGraphList() {
    const response = await GraphAdaptersRepository.fetchGraphAdapters();
    return response;
  },
  // TODO: 廃止予定
  async fetchGraphData(input: InputType) {
    return await fetchDataPoints(input);
  },
  async fetchGraphDataPoints(input: InputType): Promise<ResponseType> {
    const [graphDataPoints, graphList] = await Promise.all([
      fetchDataPoints(input),
      GraphAdaptersRepository.fetchGraphAdapters(),
    ]);

    const graphNamesMap = new Map(
      graphList.map((x) => [x.graph_no.toString(), x.graph_name])
    );

    const ret = mapValues(graphDataPoints, (dataPoints, key) => ({
      isEnabled: graphNamesMap.has(key),
      name: graphNamesMap.get(key) ?? '-',
      dataPoints: dataPoints ?? [],
    }));
    return ret;
  },
};

// 各グラフに対するデータポイントを生成する関数
const generateDataPointsForMarch = (graphNo: number): DataPointType[] => {
  const dataPoints: DataPointType[] = [];
  for (let day = 1; day <= 31; day++) {
    dataPoints.push({
      year: 2024,
      month: 3,
      date: day,
      hour: 0,
      minute: 0,
      electrical_value: 170 + graphNo * 10, // グラフ番号によって変化させる
      electrical_price: 120 + graphNo * 5,
      co2_value: 33 + graphNo * 2,
      co2_price: 60 + graphNo * 3,
      electrical_value_reduction: 7 + graphNo,
      electrical_price_reduction: 12 + graphNo,
      co2_value_reduction: 4 + graphNo,
      co2_price_reduction: 3 + graphNo,
    });
  }
  return dataPoints;
};

// モックデータの準備
const mockGraphData: ResponseType = {};

// キー1からキー16までのデータを生成
for (let i = 1; i <= 16; i++) {
  mockGraphData[i.toString()] = {
    isEnabled: true,
    name: `グラフ${i}`,
    dataPoints: generateDataPointsForMarch(i),
  };
}

// MockAdapterのインスタンスを作成し、axiosインスタンスを渡す
const mock = new MockAdapter(axios);

// 特定のAPIエンドポイントに対してモックデータを返すように設定
mock.onGet("/api/graph-data").reply(200, mockGraphData);