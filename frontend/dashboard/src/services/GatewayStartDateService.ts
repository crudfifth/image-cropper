import GatewayStartDateRepository from '@/repositories/GatewayStartDateRepository';
import UserRepository from '@/repositories/UserRepository';
import { AxiosError } from 'axios';

export default {
  async fetchGatewayStartDate(gatewayId: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    try {
      return await GatewayStartDateRepository.fetchGatewayStartDate(
        selectedCompanyId,
        gatewayId
      );
    } catch (error) {
      const e = error as AxiosError;
      if (e.status === 404) {
        return undefined;
      }
    }
  },
  async updateGatewayStartDate(gatewayId: string, startDate: Date) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    const year = startDate.getFullYear();
    const month = ('0' + (startDate.getMonth() + 1)).slice(-2);
    const day = ('0' + startDate.getDate()).slice(-2);
    return await GatewayStartDateRepository.updateGatewayStartDate(
      selectedCompanyId,
      gatewayId,
      { started_at: `${year}-${month}-${day}` }
    );
  },
};
