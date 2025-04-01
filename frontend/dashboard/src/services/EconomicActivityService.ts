import EconomicActivityRepository, {
  EconomicActivityType,
  EconomicActivityAmount,
} from '@/repositories/EconomicActivityRepository';
import UserRepository from '@/repositories/UserRepository';

export default {
  async fetchUnits() {
    return await EconomicActivityRepository.fetchUnits();
  },
  async fetchTypes() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await EconomicActivityRepository.fetchTypes(selectedCompanyId);
  },
  async fetchAmounts() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await EconomicActivityRepository.fetchAmounts(selectedCompanyId);
  },
  async isUnitSettingAvailable(year: number, month: number): Promise<boolean> {
    const amounts = await this.fetchAmounts();
    return amounts.some(amount => amount.year === year && amount.month === month);
  },
  async updateType(id: number, data: Partial<EconomicActivityType>) {
    return await EconomicActivityRepository.updateType(id, data);
  },
  async updateAmount(date: string, value: number) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No company selected');
    }
    return await EconomicActivityRepository.updateAmount(
      selectedCompanyId,
      date,
      value
    );
  },
  async updateAmounts(data: EconomicActivityAmount[]) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No company selected');
    }
    const promises = data.map((item) => {
      const dateStr = `${item.year}-${item.month
        .toString()
        .padStart(2, '0')}-01`;
      EconomicActivityRepository.updateAmount(
        selectedCompanyId,
        dateStr,
        item.value
      );
    });
    return Promise.all(promises);
  },
  async deleteAmount(date: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No company selected');
    }
    return await EconomicActivityRepository.deleteAmount(
      selectedCompanyId,
      date
    );
  },
  async deleteAmounts(data: EconomicActivityAmount[]) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No company selected');
    }
    const promises = data.map((item) => {
      const dateStr = `${item.year}-${item.month
        .toString()
        .padStart(2, '0')}-01`;
      EconomicActivityRepository.deleteAmount(selectedCompanyId, dateStr);
    });
    return Promise.all(promises);
  },
  async createType(data: Partial<EconomicActivityType>) {
    return await EconomicActivityRepository.createType(data);
  },
};
