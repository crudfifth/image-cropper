import CarbonFootprintRepository from '@/repositories/CarbonFootprintRepository';
import { CarbonFootprint } from '@/repositories/CarbonFootprintRepository';
import UserRepository from '@/repositories/UserRepository';

export type ChannelCo2Emission = {
  [key: string]: number;
};

export default {
  async fetchCarbonFootprint() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    const carbonFootprint =
      await CarbonFootprintRepository.fetchCarbonFootprint(selectedCompanyId);
    return carbonFootprint.sort((a, b) => {
      if (a.process_name < b.process_name) return -1;
      if (a.process_name > b.process_name) return 1;
      return 0;
    });
  },
  async generateGroupPieChartData(carbonFootPrint: CarbonFootprint[]) {
    const processCo2Emissions = carbonFootPrint.reduce((acc, cur) => {
      if (acc[cur.process_name]) {
        acc[cur.process_name] += cur.co2_emissions;
      } else {
        acc[cur.process_name] = cur.co2_emissions;
      }
      return acc;
    }, {} as { [key: string]: number });

    // 1, 2, 3, その他に仕分け
    // TODO: 他の箇所でも使われる処理なので、共通関数に切り出す
    const reducedEmissions = Object.entries(processCo2Emissions)
      .sort((a, b) => {
        if (a[0] < b[0]) return -1;
        if (a[0] > b[0]) return 1;
        return 0;
      })
      .sort((a, b) => b[1] - a[1])

      .reduce(
        (acc, [name, value], index, _) => {
          if (index < 3) {
            acc.values[index] = { name, value };
          } else {
            acc.others += value;
          }
          return acc;
        },
        { values: [], others: 0 } as {
          values: { name: string; value: number }[];
          others: number;
        }
      );

    const colors = ['#BAE0FD', '#FDBABA', '#FFE283', '#B2F5EA'];

    const ret = {
      labels: reducedEmissions.values
        .map((x) => x.name)
        .concat(reducedEmissions.others > 0 ? ['その他'] : []),
      datasets: [
        {
          data: reducedEmissions.values
            .map((x) => x.value)
            .concat(
              reducedEmissions.others > 0 ? [reducedEmissions.others] : []
            ),
          backgroundColor: colors.slice(
            0,
            reducedEmissions.values.length +
              (reducedEmissions.others > 0 ? 1 : 0)
          ),
        },
      ],
    };
    return ret;
  },
  async generateGroupChartData(carbonFootPrint: CarbonFootprint[]) {
    const processCo2Emissions = carbonFootPrint
      .slice()
      .sort((a, b) => {
        if (a.process_name < b.process_name) return -1;
        if (a.process_name > b.process_name) return 1;
        return 0;
      })
      .reduce((acc, cur) => {
        if (acc[cur.process_name]) {
          acc[cur.process_name] += cur.co2_emissions;
        } else {
          acc[cur.process_name] = cur.co2_emissions;
        }
        return acc;
      }, {} as { [key: string]: number });

    return {
      labels: Object.keys(processCo2Emissions),
      datasets: [
        {
          data: Object.values(processCo2Emissions),
          backgroundColor: Array(Object.keys(processCo2Emissions).length).fill(
            '#BAE0FF'
          ),
        },
      ],
    };
  },
  async fetchCarbonFootPrintScope() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    return await CarbonFootprintRepository.fetchCarbonFootPrintScope(
      selectedCompanyId
    );
  },
  async updateCarbonFootprint(
    carbonFootprint: CarbonFootprint
  ): Promise<CarbonFootprint> {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    return await CarbonFootprintRepository.updateCarbonFootprint(
      selectedCompanyId,
      carbonFootprint
    );
  },
  async deleteCarbonFootprint(carbonFootprintId: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    await CarbonFootprintRepository.deleteCarbonFootprint(
      selectedCompanyId,
      carbonFootprintId
    );
  },
  async createCarbonFootprint(
    carbonFootprint: Omit<CarbonFootprint, 'id'>
  ): Promise<CarbonFootprint> {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      throw new Error('No selected company');
    }
    return await CarbonFootprintRepository.createCarbonFootprint(
      selectedCompanyId,
      carbonFootprint
    );
  },
};
