import AnnualPlanValuesRepository, {
  AnnualPlanValues,
} from '@/repositories/AnnualPlanValuesRepository';
import UserRepository from '@/repositories/UserRepository';
import { AxiosError } from 'axios';

export default {
  async fetchAnnualPlanValues() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    try {
      return await AnnualPlanValuesRepository.fetchAnnualPlanValues(
        selectedCompanyId
      );
    } catch (error) {
      const e = error as AxiosError;
      if (e.status === 404) {
        return undefined;
      }
    }
  },
  async updateAnnualPlanValues(data: AnnualPlanValues) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    return await AnnualPlanValuesRepository.updateAnnualPlanValues(
      selectedCompanyId,
      data
    );
  },
};
