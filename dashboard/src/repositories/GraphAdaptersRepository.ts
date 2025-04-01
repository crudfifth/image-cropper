import IhiApiRepository from './IhiApiRepository';
import UserRepository from './UserRepository';
import { z } from 'zod';

const responseSchema = z.array(
  z.object({
    company_id: z.string().uuid(),
    graph_no: z.number().int(),
    graph_name: z.string(),
    gateway_id: z.string().nullable(),
    device_no: z.number().int().nullable(),
    equation_str: z.string(),
    utility_cost_price: z.number(),
    co2_emissions_current: z.number(),
    co2_emissions_baseline: z.number().nullable(),
    co2_emissions_improvement_rate: z.number(),
  })
);

export type ResponseType = z.infer<typeof responseSchema>;

export default {
  async fetchGraphAdapters() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    const response = await IhiApiRepository.get('graph_adapters/', {
      params: {
        company_id: selectedCompanyId,
      },
    });
    return responseSchema.parse(response.data);
  },
  async fetchGraphAdaptersGateway() {
    // TODO: 今どこからも呼ばれていないっぽい。どこで使う物なのだろう?
    // GraphAdapterRepository.fetchGraphAdapterGatewaysのほうが使われている。こっちはデッドコード。
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    const response = await IhiApiRepository.get('graph_adapters_gateway', {
      params: {
        company_id: selectedCompanyId,
      },
    });
    return responseSchema.parse(response.data);
  },
};
