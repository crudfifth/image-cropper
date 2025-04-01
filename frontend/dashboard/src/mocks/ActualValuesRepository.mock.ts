import MockAdapter from 'axios-mock-adapter';

export const mockActualValuesRepository = (axiosMock: MockAdapter) => {
  axiosMock.onGet(/values_electrical\/.+\/$/).reply(200, {
    actual_value: 1258.962793717,
    target_value: 361035.25,
    rate_value: 0.0034870910630388587,
  });
  axiosMock.onGet(/values_utility_costs\/.+\/$/).reply(200, {
    actual_value: 125896.27937166701,
    target_value: 10287.083333333334,
    rate_value: 12.238287111345166,
  });
  axiosMock.onGet(/values_co2emissions\/.+\/$/).reply(200, {
    actual_value: 251.79255874299997,
    target_value: 6.083333333333333,
    rate_value: 41.39055760158904,
  });
  axiosMock.onGet(/values_carbon_credit\/.+\/$/).reply(200, {
    actual_value: 50358.511748667006,
    target_value: 0.3333333333333333,
    rate_value: 151075.53524600103,
  });
};
