import { HistoryItem, UnitPrice } from '@/types';
import IhiApiRepository from './IhiApiRepository';

export default {
  async fetchHistoryItems(
    companyId: string,
    field?: string
  ): Promise<HistoryItem[]> {
    const { data } = await IhiApiRepository.get(`unit_price_history/`, {
      params: {
        company_id: companyId,
        field: field ? field : undefined,
      },
    });
    return data;
  },
  async fetchLatestUnitPrice(companyId: string): Promise<UnitPrice> {
    const { data } = await IhiApiRepository.get(`latest_unit_price/`, {
      params: {
        company_id: companyId,
      },
    });
    return data;
  },
  async createUnitPriceHistory(body: {
    company_id: string;
    field: string;
    name: string;
    before: number;
    after: number;
  }) {
    const { data } = await IhiApiRepository.post(`unit_price_history/`, body);
    return data;
  },
};
