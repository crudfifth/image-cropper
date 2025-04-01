import { graphStateStore } from '@/stores/TrendGraphStore';
import { EnergyType } from '@/types';
import { TrendGraphType } from '@/types';
import { match } from 'ts-pattern';

// TODO: 廃止予定
export const createEnergyTypeTitleText = (input: {
  energyType: EnergyType;
}): string => {
  switch (input.energyType) {
    case 'utilityCost': {
      return '光熱費';
    }
    case 'electricity': {
      return '電力量';
    }
    case 'co2': {
      return 'CO₂量';
    }
    default: {
      const unreachable: never = input.energyType; // eslint-disable-line
      return '';
    }
  }
};

// TODO: 廃止予定
export const createEnergyTypeUnitLabelText = (input: {
  energyType: EnergyType;
}): string => {
  switch (input.energyType) {
    case 'utilityCost': {
      return '円';
    }
    case 'electricity': {
      return 'kWh';
    }
    case 'co2': {
      return 't/h';
    }
    default: {
      const unreachable: never = input.energyType; // eslint-disable-line
      return '';
    }
  }
};

const createElectricityLabelText = () =>
  graphStateStore.intensity === 'intensity' ? 'kWh/原単位' : 'kWh';

const createCurrencyLabelText = () =>
  graphStateStore.intensity === 'intensity' ? '円/原単位' : '円';

const createCo2TonLabelText = () =>
  graphStateStore.intensity === 'intensity' ? 't-CO₂e/原単位' : 't-CO₂e';

const createCo2KgLabelText = () =>
  graphStateStore.intensity === 'intensity' ? 'kg-CO₂e/原単位' : 'kg-CO₂e';

const createCo2LabelText = (isKgUnit: boolean) => {
  return isKgUnit ? createCo2KgLabelText() : createCo2TonLabelText();
};

export const createGraphUnitLabelText = (input: {
  graphType: TrendGraphType;
  isKgUnit: boolean;
}): string =>
  match(input.graphType)
    .with('electricity', createElectricityLabelText)
    .with('utilityCost', createCurrencyLabelText)
    .with('co2Emission', () => createCo2LabelText(input.isKgUnit))
    .with('carbonCredit', createCurrencyLabelText)
    .with('electricityReduction', createElectricityLabelText)
    .with('utilityCostReduction', createCurrencyLabelText)
    .with('co2EmissionReduction', () => createCo2LabelText(input.isKgUnit))
    .with('carbonFootprint', createElectricityLabelText)
    .exhaustive();
