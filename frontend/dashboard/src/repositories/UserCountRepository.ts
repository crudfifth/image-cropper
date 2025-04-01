import { z } from 'zod';
import IhiApiRepository from './IhiApiRepository';
import UserRepository from './UserRepository';

export type UserCount = {
  user_limit: number;
  user_count: number;
  active_user_count: number;
};

const registeredUserCountSchema = z.object({
  user_limit: z.number().int(),
  user_count: z.number().int(),
  active_user_count: z.number().int(),
});


export default {
  async fetchRegisteredUserCount(): Promise<UserCount> {
    const companyId = await UserRepository.getSelectedCompanyId();
    const response = await IhiApiRepository.get(`registered_user_count/${companyId}/`);
    return registeredUserCountSchema.parse(response.data);
  }
};
