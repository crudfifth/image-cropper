import GraphAdapterRepository, {
  GraphAdapter,
} from '@/repositories/GraphAdapterRepository';
import UserRepository from '@/repositories/UserRepository';
import { roundTwoDecimal } from '@/utils/Round';

export default {
  async fetchChannelDataList() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();

    const graphAdapters = await GraphAdapterRepository.fetchGraphAdapters(
      selectedCompanyId
    );
    return graphAdapters.map((graphAdapter) => {
      return {
        id: graphAdapter.graph_no,
        name: graphAdapter.graph_name,
        currentdata: graphAdapter.co2_emissions_current,
        ratio: graphAdapter.co2_emissions_improvement_rate,
        selectedGateway: graphAdapter.gateway_id,
        selectedChannel: graphAdapter.device_no,
        formula: graphAdapter.equation_str,
        unitPrice: graphAdapter.utility_cost_price,
        baseline: graphAdapter.co2_emissions_baseline,
        improvementRate: roundTwoDecimal(
          // TODO: 本来はcomputed Propertyを使って表示の時点で%に直すべき
          graphAdapter.co2_emissions_improvement_rate * 100
        ),
        isCo2EmissionsBaseline: graphAdapter.is_co2_emissions_baseline,
      };
    });
  },
  async fetchGraphAdapterGateways() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    const gateways = await GraphAdapterRepository.fetchGraphAdapterGateways(
      selectedCompanyId
    );
    return gateways.map((gateway) => {
      return {
        ...gateway,
        gateway_id: String(gateway.gateway_id),
      };
    });
  },
  async updateGraphAdapters(graphAdapters: Partial<GraphAdapter>[]) {
    const promises = graphAdapters.map((graphAdapter) => {
      if (graphAdapter.graph_no) {
        return this.updateGraphAdapter(graphAdapter.graph_no, graphAdapter);
      }
    });
    await Promise.all(promises);
  },
  async updateGraphAdapter(graphNo: number, data: Partial<GraphAdapter>) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    return await GraphAdapterRepository.updateGraphAdapter(
      selectedCompanyId,
      graphNo,
      {
        ...data,
        // TODO: ここも本来はcomputed Propertyを使って表示の時点で%に直すべき
        co2_emissions_improvement_rate: data.co2_emissions_improvement_rate
          ? data.co2_emissions_improvement_rate / 100
          : 0,
      }
    );
  },
  async deleteGraphAdapterList(graphNos: number[]) {
    const promises = graphNos.map((graphNo) =>
      this.deleteGraphAdapter(graphNo)
    );
    await Promise.all(promises);
  },
  async deleteGraphAdapter(graphNo: number) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    return await GraphAdapterRepository.deleteGraphAdapter(
      selectedCompanyId,
      graphNo
    );
  },
  async isGatewayUsedInTrendGraph(gatewayId: string): Promise<boolean> {
    const channelDataList = await this.fetchChannelDataList();
    return channelDataList.some( channel => channel.selectedGateway === gatewayId );
  },
};
