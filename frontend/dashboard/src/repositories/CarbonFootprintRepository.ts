import IhiApiRepository from '@/repositories/IhiApiRepository';

export type CarbonFootprint = {
  id: string;
  process_name: string;
  channel_name: string;
  start_date: string | undefined;
  end_date: string | undefined;
  electric_value: number;
  co2_emissions: number;
  scope_no: number;
};

export type CarbonFootprintScope = {
  ghg_emmision: number;
  scope1: number;
  scope2: number;
  scope3: number;
};


export default {
  async fetchCarbonFootprint(companyId: string): Promise<CarbonFootprint[]> {
    const { data } = await IhiApiRepository.get(
      `carbon_footprint/${companyId}/`
    );
    return data;
  },
  async fetchCarbonFootPrintScope(companyId: string): Promise<CarbonFootprintScope> {
    const { data } = await IhiApiRepository.get(
      `carbon_footprint_scope/${companyId}/`
    );
    return data;
  },
  async updateCarbonFootprint(
    companyId: string,
    carbonFootprint: CarbonFootprint
  ): Promise<CarbonFootprint> {
    const { data } = await IhiApiRepository.patch(
      `carbon_footprint/${companyId}/${carbonFootprint.id}/`,
      carbonFootprint
    );
    return data;
  },
  async deleteCarbonFootprint(
    companyId: string,
    carbonFootprintId: string
  ): Promise<void> {
    await IhiApiRepository.delete(
      `carbon_footprint/${companyId}/${carbonFootprintId}/`
    );
  },
  async createCarbonFootprint(
    companyId: string,
    carbonFootprint: Omit<CarbonFootprint, 'id'>
  ): Promise<CarbonFootprint> {
    const { data } = await IhiApiRepository.post(
      `carbon_footprint/${companyId}/`,
      carbonFootprint
    );
    return data;
  }
};
