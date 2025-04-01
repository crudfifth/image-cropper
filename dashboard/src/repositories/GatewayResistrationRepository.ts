import IhiApiRepository from './IhiApiRepository';
import { z } from 'zod';
import UserRepository from './UserRepository';
import { AxiosError, isAxiosError } from 'axios';

const gatewaySchema = z.object({
  company_id: z.string().uuid(),
  graph_no: z.number().int(),
  graph_name: z.string(),
  gateway_id: z.string(),
  device_no: z.number().int(),
  equation_str: z.string(),
  utility_cost_price: z.number(),
  co2_emissions_current: z.number(),
  co2_emissions_baseline: z.number().nullable(),
  co2_emissions_improvement_rate: z.number(),
});

const gatewayListSchema = z
  .object({
    type: z.string(),
    name: z.string(),
    id: z.string(),
    license_limit: z.string(),
    license_type: z.string(),
    signal_level: z.number().int(),
    connected: z.boolean(),
    updated_at: z.string(),
  })
  .array();

const registeredGatewayCountSchema = z.object({
  gateway_limit: z.number().int(),
  gateway_count: z.number().int(),
  operations_count: z.number().int(),
});

export type SingleResponseType = z.infer<typeof gatewaySchema>;
export type ListResponseType = z.infer<typeof gatewayListSchema>;
export type RegisteredGatewayCountType = z.infer<
  typeof registeredGatewayCountSchema
>;

export default {
  createGatewayRegistration: async (input: { id: string; name: string }) => {
    const companyId = await UserRepository.getSelectedCompanyId();
    try {
      return await IhiApiRepository.post(
        `gateway_registration/${companyId}/${input.id}/`,
        {
          gateway_name: input.name,
        }
      );
    } catch (error) {
      if (isAxiosError(error)) {
        return {
          error: error,
        };
      }
      return {
        error: error as AxiosError,
      };
    }
  },
  fetchGatewayRegistration: async (input: { id: string }) => {
    const companyId = await UserRepository.getSelectedCompanyId();
    const response = await IhiApiRepository.get(
      `gateway_registration/${companyId}/${input.id}/`
    );
    return gatewaySchema.parse(response);
  },
  deleteGatewayRegistration: async (input: { id: string }) => {
    const companyId = await UserRepository.getSelectedCompanyId();
    return await IhiApiRepository.delete(
      `gateway_registration/${companyId}/${input.id}/`
    );
  },
  fetchGatewayRegistrationList: async () => {
    const response = await IhiApiRepository.get(`gateway_registration/`);
    return gatewayListSchema.parse(response.data);
  },
  fetchRegisteredGatewayCount: async () => {
    const companyId = await UserRepository.getSelectedCompanyId();
    const response = await IhiApiRepository.get(
      `registered_gateway_count/${companyId}/`
    );
    return registeredGatewayCountSchema.parse(response.data);
  },
};
