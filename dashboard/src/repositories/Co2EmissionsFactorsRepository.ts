import IhiApiRepository from './IhiApiRepository';

export type Co2EmissionsFactors = {
  name: string;
  no: number;
  factor: number;
  region_name: string;
}[];

export default {
  async fetchCo2EmissionsFactors(): Promise<Co2EmissionsFactors> {
    const { data } = await IhiApiRepository.get('co2emissions_factors/');
    return data;
  }
};
