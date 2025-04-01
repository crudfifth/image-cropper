import GraphReductionsRepository from '@/repositories/GraphReductionsRepository';
import UserRepository from '@/repositories/UserRepository';
import {
  InputType as RepositoryInputType,
  ResponseType as RepositoryResponseType,
} from '@/repositories/GraphReductionsRepository';

export type InputType = Omit<RepositoryInputType, 'companyId'>;
export type ResponseType = RepositoryResponseType;

export default {
  async fetchGraphDataReductions(input: InputType) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return GraphReductionsRepository.fetchGraphDataReductions({
      ...input,
      companyId: selectedCompanyId,
    });
  },
};
