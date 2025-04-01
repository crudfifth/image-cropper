import IhiApiRepository from './IhiApiRepository';
import UserRepository from './UserRepository';
import { z } from 'zod';

const predictionsSchema = z.object({
  monthly_prediction_value: z.number(),
  yearly_prediction_value: z.number(),
  yearly_target_value: z.number(),
  yearly_improvement_rate: z.number(),
});

export default {
  async fetchPredictedValuesElectrical() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `prediction_electrical/${companyId}/`
    );
    return predictionsSchema.parse(data);
  },
  async fetchPredictedValuesUtilityCosts() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `prediction_utility_costs/${companyId}/`
    );
    // 年間計画値がyearly_target_priceになっているようなので、yearly_target_valueに詰め直すワークアラウンド
    if (
      data.yearly_target_price !== undefined &&
      data.yearly_target_value === undefined
    ) {
      data.yearly_target_value = data.yearly_target_price;
      delete data.yearly_target_price;
    }
    return predictionsSchema.parse(data);
  },
  async fetchPredictedValuesCo2Emissions() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `prediction_co2emissions/${companyId}/`
    );
    return predictionsSchema.parse(data);
  },
  async fetchPredictedValuesCarbonCredit() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `prediction_carbon_credit/${companyId}/`
    );
    return predictionsSchema.parse(data);
  },
  async fetchPredictedValuesReductionElectrical() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `prediction_reduction_electrical/${companyId}/`
    );
    return predictionsSchema.parse(data);
  },
  async fetchPredictedValuesReductionUtilityCosts() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `prediction_reduction_utility_costs/${companyId}/`
    );
    // 年間計画値がyearly_target_priceになっているようなので、yearly_target_valueに詰め直すワークアラウンド
    if (
      data.yearly_target_price !== undefined &&
      data.yearly_target_value === undefined
    ) {
      data.yearly_target_value = data.yearly_target_price;
      delete data.yearly_target_price;
    }
    return predictionsSchema.parse(data);
  },
  async fetchPredictedValuesReductionCo2Emissions() {
    const companyId = await UserRepository.getSelectedCompanyId();
    const { data } = await IhiApiRepository.get(
      `prediction_reduction_co2emissions/${companyId}/`
    );
    return predictionsSchema.parse(data);
  },
};
