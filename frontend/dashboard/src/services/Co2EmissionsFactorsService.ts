import Co2EmissionsFactorsRepository from "@/repositories/Co2EmissionsFactorsRepository";

export default {
  async fetchCo2EmissionsFactorValues() {
    return await Co2EmissionsFactorsRepository.fetchCo2EmissionsFactors();
  }
};
