import MonthlyCostTargetRepository from '@/repositories/MonthlyCostTargetRepository';
import UserRepository from '@/repositories/UserRepository';

export default {
  async fetchMonthlyCostTargets({
    year,
    month,
    targetType,
  }: {
    year?: number;
    month?: number;
    targetType?: string;
  } = {}) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await MonthlyCostTargetRepository.fetchMonthlyCostTargets({
      year,
      month,
      target_type: targetType,
      company_id: selectedCompanyId,
    });
  },
  async updateMonthlyCostTarget({
    year,
    month,
    targetType,
    targetValue,
    targetPrice,
  }: {
    year: number;
    month: number;
    targetType: string;
    targetValue: number;
    targetPrice: number;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    return await MonthlyCostTargetRepository.updateMonthlyCostTarget({
      year,
      month,
      target_type: targetType,
      target_value: targetValue,
      target_price: targetPrice,
      company_id: selectedCompanyId,
    });
  },
};
