import IhiApiRepository from '@/repositories/IhiApiRepository';

// TODO: GraphAdapter"s" Repositoryが別にある。紛らわしいのであとで統一する

export type GraphAdapter = {
  graph_name: string;
  graph_no: number;
  co2_emissions_baseline: number;
  co2_emissions_current: number;
  co2_emissions_improvement_rate: number;
  company_id: string;
  device_no: number;
  equation_str: string;
  gateway_id: string | null;
  utility_cost_price: number;
  is_co2_emissions_baseline: boolean;
};

export type GraphAdapterGateway = {
  gateway_id: string;
  name: string;
  devices: number[];
  enable_devices: [number, string][];
  device_names: [number, string][];
};

export default {
  async fetchGraphAdapters(
    companyId: string | undefined
  ): Promise<GraphAdapter[]> {
    const { data } = await IhiApiRepository.get('graph_adapters/', {
      params: {
        company_id: companyId,
      },
    });
    return data;
  },
  async fetchGraphAdapterGateways(
    companyId: string | undefined
  ): Promise<GraphAdapterGateway[]> {
    const { data } = await IhiApiRepository.get('graph_adapters_gateway/', {
      params: {
        company_id: companyId,
      },
    });
    return data;
  },
  async updateGraphAdapter(
    companyId: string,
    graphNo: number,
    body: Partial<GraphAdapter>
  ) {
    const { data } = await IhiApiRepository.patch(
      `graph_adapters/${companyId}/${graphNo}/`,
      body
    );
    return data;
  },
  async deleteGraphAdapter(companyId: string, graphNo: number) {
    const { data } = await IhiApiRepository.delete(
      `graph_adapters/${companyId}/${graphNo}/`
    );
    return data;
  },
};
