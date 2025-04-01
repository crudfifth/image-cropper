import { GraphKeyType, DataPointType, ResponseType } from '@/services/GraphService';
import MockAdapter from 'axios-mock-adapter';
import axios from 'axios';

const generateDataPointsForMarch = (graphNo: number): DataPointType[] => {
  const dataPoints: DataPointType[] = [];
  for (let day = 1; day <= 31; day++) {
    dataPoints.push({
      year: 2024,
      month: 3,
      date: day,
      hour: 0,
      minute: 0,
      electrical_value: 170 + graphNo,
      electrical_price: 120 + graphNo,
      co2_value: 33 + graphNo,
      co2_price: 60 + graphNo,
      electrical_value_reduction: 7 + graphNo,
      electrical_price_reduction: 12 + graphNo,
      co2_value_reduction: 4 + graphNo,
      co2_price_reduction: 3 + graphNo,
    });
  }
  return dataPoints;
};

const mockGraphData: ResponseType = {};

for (let i = 1; i <= 16; i++) {
  const graphNoAsString: keyof ResponseType = i.toString() as keyof ResponseType;
  mockGraphData[graphNoAsString] = {
    isEnabled: true,
    name: `グラフ${i}`,
    dataPoints: generateDataPointsForMarch(i),
  };
}

const mock = new MockAdapter(axios);
mock.onGet('/api/graph-data').reply(200, mockGraphData);

export default mockGraphData;