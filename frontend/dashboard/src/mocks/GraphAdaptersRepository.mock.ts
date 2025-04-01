import MockAdapter from 'axios-mock-adapter';
import { ResponseType } from '@/repositories/GraphAdaptersRepository';

export const mockGraphAdaptersRepository = (mock: MockAdapter) => {
  const mockGraphAdaptersData: ResponseType = [
    {
      company_id: '123e4567-e89b-12d3-a456-426614174000',
      graph_no: 1,
      graph_name: 'グラフA',
      gateway_id: null,
      device_no: null,
      equation_str: '(x)',
      utility_cost_price: 100,
      co2_emissions_current: 200,
      co2_emissions_baseline: null,
      co2_emissions_improvement_rate: 5,
    },
    {
      company_id: '123e4567-e89b-12d3-a456-426614174001',
      graph_no: 2,
      graph_name: 'グラフB',
      gateway_id: 'gateway_01',
      device_no: 1,
      equation_str: '(x)',
      utility_cost_price: 150,
      co2_emissions_current: 250,
      co2_emissions_baseline: 100,
      co2_emissions_improvement_rate: 10,
    },
    {
      company_id: '123e4567-e89b-12d3-a456-426614174001',
      graph_no: 3,
      graph_name: 'グラフC',
      gateway_id: 'gateway_01',
      device_no: 1,
      equation_str: '(x)',
      utility_cost_price: 150,
      co2_emissions_current: 250,
      co2_emissions_baseline: 100,
      co2_emissions_improvement_rate: 10,
    },
  ];

  mock.onGet('/graph_adapters/').reply(200, mockGraphAdaptersData);

  const mockGraphAdaptersGatewayData: ResponseType = [
    // {
    //   gateway_id: 'gateway_01',
    //   graph_name: 'ゲートウェイ1',
    //   devices: [1, 2, 3],
    //   enable_devices: [
    //     [1, 'デバイス1'],
    //     [2, 'デバイス2'],
    //   ],
    //   device_names: [
    //     [1, 'デバイス1'],
    //     [2, 'デバイス2'],
    //     [3, 'デバイス3'],
    //   ],
    // },
    // {
    //   gateway_id: 'gateway_02',
    //   name: 'ゲートウェイ2',
    //   devices: [4, 5, 6],
    //   enable_devices: [
    //     [4, 'デバイス4'],
    //     [5, 'デバイス5'],
    //   ],
    //   device_names: [
    //     [4, 'デバイス4'],
    //     [5, 'デバイス5'],
    //     [6, 'デバイス6'],
    //   ],
    // },
  ];

  mock
    .onGet('/graph_adapters_gateway')
    .reply(200, mockGraphAdaptersGatewayData);
};
