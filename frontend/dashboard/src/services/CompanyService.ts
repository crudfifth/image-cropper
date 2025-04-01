import CompanyRepository from '@/repositories/CompanyRepository';
import UserRepository from '@/repositories/UserRepository';

export default {
  updateUnit(id: string, unitId: string) {
    return CompanyRepository.update(id, {
      economic_activity_unit: unitId,
    });
  },
  fetchCompanies() {
    return CompanyRepository.fetchCompanies();
  },
  async fetchIsCompanyAdmin(companyId: string): Promise<boolean> {
    const res = await CompanyRepository.fetchIsCompanyAdmin(companyId);
    return res.is_admin;
  },
  async fetchSelectedCompany() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return undefined;
    }
    return await CompanyRepository.fetchCompany(selectedCompanyId);
  },
};
