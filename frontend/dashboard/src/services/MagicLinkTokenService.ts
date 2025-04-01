import MagicLinkTokenRepository from '@/repositories/MagicLinkTokenRepository';
import type {
  fetchUserInputType,
  activateUserInputType,
} from '@/repositories/MagicLinkTokenRepository';

export default {
  fetchUserByActivationToken: async (input: fetchUserInputType) => {
    return MagicLinkTokenRepository.fetchUserByActivationToken(input);
  },
  activateUser: async (input: activateUserInputType) => {
    return MagicLinkTokenRepository.activateUser(input);
  },
};
