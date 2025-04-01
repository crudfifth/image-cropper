import PredictedValuesRepository from '@/repositories/PredictedValuesRepository';

export default {
  async fetchPredictedValuesElectrical() {
    return PredictedValuesRepository.fetchPredictedValuesElectrical();
  },
  async fetchPredictedValuesUtilityCosts() {
    return PredictedValuesRepository.fetchPredictedValuesUtilityCosts();
  },
  async fetchPredictedValuesCo2Emissions() {
    return PredictedValuesRepository.fetchPredictedValuesCo2Emissions();
  },
  async fetchPredictedValuesCarbonCredit() {
    return PredictedValuesRepository.fetchPredictedValuesCarbonCredit();
  },
  async fetchPredictedValuesReductionElectrical() {
    return PredictedValuesRepository.fetchPredictedValuesReductionElectrical();
  },
  async fetchPredictedValuesReductionUtilityCosts() {
    return PredictedValuesRepository.fetchPredictedValuesReductionUtilityCosts();
  },
  async fetchPredictedValuesReductionCo2Emissions() {
    return PredictedValuesRepository.fetchPredictedValuesReductionCo2Emissions();
  },
};
