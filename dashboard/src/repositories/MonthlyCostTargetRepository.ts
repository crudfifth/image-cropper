import IhiApiRepository from '@/repositories/IhiApiRepository';

export type Target = {
  id: number;
  year: number;
  month: number;
  target_type: string;
  target_value: number;
  target_price: number;
  user_id: string;
};

type FetchListParams = {
  year?: number;
  month?: number;
  target_type?: string;
  company_id?: string;
};

type PutParams = {
  year: number;
  month: number;
  target_type: string;
  target_value: number;
  target_price: number;
  company_id: string;
};

export default {
  async fetchMonthlyCostTargets(
    params: FetchListParams = {}
  ): Promise<Target[]> {
    const { data } = await IhiApiRepository.get('monthly_cost_targets/', {
      params: {
        ...(params.year && { year: String(params.year) }),
        ...(params.month && { month: String(params.month) }),
        target_type: params.target_type,
        company_id: params.company_id,
      },
    });
    return data;
  },
  async updateMonthlyCostTarget(params: PutParams): Promise<Target> {
    const { data } = await IhiApiRepository.put(
      `monthly_cost_targets/${params.company_id}/${params.year}/${params.month}/${params.target_type}/`,
      {
        target_value: params.target_value,
        target_price: params.target_price,
      }
    );
    return data;
  },
};
