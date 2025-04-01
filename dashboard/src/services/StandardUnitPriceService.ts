import StandardUnitPriceRepository from '@/repositories/StandardUnitPriceRepository';
import UserRepository from '@/repositories/UserRepository';

export default {
  async fetchHistoryItems(field?: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return [];
    }
    return StandardUnitPriceRepository.fetchHistoryItems(
      selectedCompanyId,
      field
    );
  },
  async fetchLatestUnitPrice() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return undefined;
    }
    return StandardUnitPriceRepository.fetchLatestUnitPrice(selectedCompanyId);
  },
  async createUnitPriceHistory(body: {
    field: string;
    name: string;
    before: number;
    after: number;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return undefined;
    }
    return StandardUnitPriceRepository.createUnitPriceHistory({
      company_id: selectedCompanyId,
      ...body,
    });
  },
};
