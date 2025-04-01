import IhiApiRepository from '@/repositories/IhiApiRepository';
import { z } from 'zod';

const annualPlanValuesSchema = z.object({
  utility_cost: z.number(),
  utility_cost_reduce: z.number(),
  electric: z.number(),
  electric_reduce: z.number(),
  co2_emissions: z.number(),
  co2_emissions_reduce: z.number(),
  carbon_credit_price: z.number(),
  carbon_credit: z.number(),
});

export type AnnualPlanValues = z.infer<typeof annualPlanValuesSchema>;

export default {
  async fetchAnnualPlanValues(companyId: string): Promise<AnnualPlanValues> {
    const { data } = await IhiApiRepository.get(
      `annual_plan_values/${companyId}/`
    );
    return annualPlanValuesSchema.parse(data);
  },
  async updateAnnualPlanValues(
    companyId: string,
    body: Partial<AnnualPlanValues>
  ) {
    const { data } = await IhiApiRepository.patch(
      `annual_plan_values/${companyId}/`,
      body
    );
    return data;
  },
};
