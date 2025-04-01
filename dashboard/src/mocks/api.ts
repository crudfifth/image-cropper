import axiosInstance from '@/repositories/IhiApiRepository';
import MockAdapter from 'axios-mock-adapter';
import { mockActualValuesRepository } from './ActualValuesRepository.mock';
import { mockAnnualPlanValuesRepository } from './AnnualPlanValuesRepository.mock';
import { mockGraphAdaptersRepository } from './GraphAdaptersRepository.mock';

// MagicLink系APIはAxiosのインスタンス自体が違うので別にインポート
import { axiosInstance as magicLinkInstance } from '@/repositories/MagicLinkTokenRepository';
import { mockMagicLinkTokenRepository } from './MagicLinkTokenRepsitory.mock';

export const enableMock = () => {
  const mock = new MockAdapter(axiosInstance);

  mockActualValuesRepository(mock);
  mockAnnualPlanValuesRepository(mock);
  mockGraphAdaptersRepository(mock);

  mock.onAny().passThrough();

  const magicLinkMock = new MockAdapter(magicLinkInstance);
  mockMagicLinkTokenRepository(magicLinkMock);
  magicLinkMock.onAny().passThrough();
};
