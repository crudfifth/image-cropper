import GatewayRegistrationRepository from '@/repositories/GatewayResistrationRepository';

export default {
  createGateway: async (input: { id: string; name: string }) => {
    // TODO: エラー処理
    return await GatewayRegistrationRepository.createGatewayRegistration(input);
  },
  fetchGateway: async (input: { id: string }) => {
    return await GatewayRegistrationRepository.fetchGatewayRegistration(input);
  },
  deleteGateway: async (input: { id: string }) => {
    return await GatewayRegistrationRepository.deleteGatewayRegistration(input);
  },
  fetchGatewayList: async () => {
    return await GatewayRegistrationRepository.fetchGatewayRegistrationList();
  },
  fetchRegisterdGatewayCount: async () => {
    return await GatewayRegistrationRepository.fetchRegisteredGatewayCount();
  },
};
