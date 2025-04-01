import { Company, IsCompanyAdmin } from '@/types';
import IhiApiRepository from './IhiApiRepository';

export default {
  async update(id: string, params: Partial<Company>): Promise<Company[]> {
    const { data } = await IhiApiRepository.patch(`companies/${id}/`, params);
    return data;
  },
  async fetchCompanies(): Promise<Company[]> {
    const { data } = await IhiApiRepository.get('companies/');
    return data;
  },
  async fetchIsCompanyAdmin(companyId: string): Promise<IsCompanyAdmin> {
    const { data } = await IhiApiRepository.get(
      `companies/${companyId}/is_admin/`
    );
    return data;
  },
  async fetchCompany(companyId: string): Promise<Company> {
    const { data } = await IhiApiRepository.get(`companies/${companyId}/`);
    return data;
  },
};
