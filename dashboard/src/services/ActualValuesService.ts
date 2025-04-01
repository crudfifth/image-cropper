import ActualValuesRepository from '@/repositories/ActualValuesRepository';

export default {
  async fetchValuesElectrical() {
    return ActualValuesRepository.fetchValuesElectrical();
  },
  async fetchValuesUtilityCosts() {
    return ActualValuesRepository.fetchValuesUtilityCosts();
  },
  async fetchValuesCo2Emissions() {
    return ActualValuesRepository.fetchValuesCo2Emissions();
  },
  async fetchValuesCarbonCredit() {
    return ActualValuesRepository.fetchValuesCarbonCredit();
  },
  async fetchValuesReductionElectrical() {
    return ActualValuesRepository.fetchValuesReductionElectrical();
  },
  async fetchValuesReductionUtilityCosts() {
    return ActualValuesRepository.fetchValuesReductionUtilityCosts();
  },
  async fetchValuesReductionCo2Emissions() {
    return ActualValuesRepository.fetchValuesReductionCo2Emissions();
  },
};
