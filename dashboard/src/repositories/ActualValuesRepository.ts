import IhiApiRepository from './IhiApiRepository';
import UserRepository from './UserRepository';
import { z } from 'zod';

const valuesSchema = z.object({
  actual_value: z.number(),
  target_value: z.number(),
  rate_value: z.number(),
});

export default {
  async fetchValuesElectrical() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `values_electrical/${companyId}/`
    );
    return valuesSchema.parse(data);
  },
  async fetchValuesUtilityCosts() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `values_utility_costs/${companyId}/`
    );
    return valuesSchema.parse(data);
  },
  async fetchValuesCo2Emissions() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `values_co2emissions/${companyId}/`
    );
    return valuesSchema.parse(data);
  },
  async fetchValuesCarbonCredit() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `values_carbon_credit/${companyId}/`
    );
    return valuesSchema.parse(data);
  },
  async fetchValuesReductionElectrical() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `reduction_electrical/${companyId}/`
    );
    return valuesSchema.parse(data);
  },
  async fetchValuesReductionUtilityCosts() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `reduction_utility_costs/${companyId}/`
    );
    return valuesSchema.parse(data);
  },
  async fetchValuesReductionCo2Emissions() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `reduction_co2emissions/${companyId}/`
    );
    return valuesSchema.parse(data);
  },
};
