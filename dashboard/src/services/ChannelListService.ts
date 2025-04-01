import IhiApiRepository from '../repositories/IhiApiRepository';
import UserRepository from '@/repositories/UserRepository';

export type FetchChannelOutputType = Map<string, string>;

export default {
  async fetchChannelNamesMap() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();

    // 急ぎの実装なのでService側で直接fetchする
    const requests = Array.from({ length: 16 }, (_, i) => i + 1).map(
      (graph_no) =>
        IhiApiRepository.get('channel/', {
          params: {
            graph_no,
            company_id: selectedCompanyId,
          },
        })
    );

    const responses = await Promise.all(requests);

    const channelNameMap = new Map(
      responses
        .filter(
          (response) => response.data.graph_no && response.data.graph_name
        )
        .map((response) => [
          response.data.graph_no?.toString(),
          response.data.graph_name,
        ])
    );
    return channelNameMap;
  },
};
