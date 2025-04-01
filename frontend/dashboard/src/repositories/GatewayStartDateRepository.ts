import IhiApiRepository from '@/repositories/IhiApiRepository';

export type GatewayStartDate = {
  gateway_id: string;
  started_at: string;
};

export default {
  async fetchGatewayStartDate(
    companyId: string,
    gatewayId: string
  ): Promise<GatewayStartDate | undefined> {
    const { data } = await IhiApiRepository.get(
      `gateway_startdate/${companyId}/${gatewayId}/`
    );
    return data;
  },
  async updateGatewayStartDate(
    companyId: string,
    gatewayId: string,
    body: { started_at: string }
  ): Promise<GatewayStartDate> {
    const { data } = await IhiApiRepository.post(
      `gateway_startdate/${companyId}/${gatewayId}/`,
      body
    );
    return data;
  },
};
