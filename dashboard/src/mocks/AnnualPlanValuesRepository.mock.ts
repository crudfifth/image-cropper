import MockAdapter from 'axios-mock-adapter';

export const mockAnnualPlanValuesRepository = (axiosMock: MockAdapter) => {
  axiosMock.onGet(/annual_plan_values\/.+\/$/).reply(200, {
    utility_cost: 12344.0,
    electric: 4332423.0,
    electric_reduce: 9.0,
    co2_emissions: 73.0,
    co2_emissions_reduce: 4.0,
    carbon_credit: 4.0,
    carbon_credit_price: 1.0,
  });
  axiosMock.onPatch(/annual_plan_values\/.+\/$/).reply(200, {
    utility_cost: 12344.0,
    electric: 4332423.0,
    electric_reduce: 9.0,
    co2_emissions: 73.0,
    co2_emissions_reduce: 4.0,
    carbon_credit: 4.0,
    carbon_credit_price: 1.0,
  });
};
