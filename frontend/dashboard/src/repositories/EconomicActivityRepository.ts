import IhiApiRepository from './IhiApiRepository';

export type EconomicActivityUnit = {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
};

export type EconomicActivityType = {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
};

export type EconomicActivityAmount = {
  year: number;
  month: number;
  value: number;
};

export default {
  async fetchUnits(): Promise<EconomicActivityUnit[]> {
    const { data } = await IhiApiRepository.get('economic_activity_units/');
    return data;
  },
  async fetchTypes(companyId?: string): Promise<EconomicActivityType[]> {
    const { data } = await IhiApiRepository.get('economic_activity_types/', {
      params: {
        company_id: companyId,
      },
    });
    return data;
  },
  async fetchAmounts(companyId?: string): Promise<EconomicActivityAmount[]> {
    const { data } = await IhiApiRepository.get('economic_activity_amounts/', {
      params: {
        company_id: companyId,
      },
    });
    return data;
  },
  async updateType(
    id: number,
    data: Partial<EconomicActivityType>
  ): Promise<EconomicActivityType> {
    const { data: response } = await IhiApiRepository.patch(
      `economic_activity_types/${id}/`,
      data
    );
    return response;
  },
  async updateAmount(
    companyId: string,
    date: string,
    value: number
  ): Promise<EconomicActivityAmount> {
    const { data: response } = await IhiApiRepository.put(
      `companies/${companyId}/economic_activity_amounts/${date}/`,
      {
        value,
      }
    );
    return response;
  },
  async deleteAmount(
    companyId: string,
    date: string
  ): Promise<EconomicActivityAmount> {
    const { data: response } = await IhiApiRepository.delete(
      `companies/${companyId}/economic_activity_amounts/${date}/`
    );
    return response;
  },
  async createType(
    data: Partial<EconomicActivityType>
  ): Promise<EconomicActivityType> {
    const { data: response } = await IhiApiRepository.post(
      'economic_activity_types/',
      data
    );
    return response;
  },
};
