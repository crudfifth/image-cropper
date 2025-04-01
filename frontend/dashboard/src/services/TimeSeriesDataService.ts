import UserRepository from '@/repositories/UserRepository';
import TimeSeriesDataRepository from '../repositories/TimeSeriesDataRepository';

type fuelUnitType = 'm3' | 'L' | 'kg';

export default {
  async fetchHourlyData({
    year,
    month,
    date,
    mode = undefined,
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    month: number;
    date: number;
    mode?: string;
    activityTypeId?: string;
    fuelUnit?: fuelUnitType;
    entityId?: string;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await TimeSeriesDataRepository.fetchHourlyData({
      year,
      month,
      date,
      mode,
      activityTypeId,
      companyId: selectedCompanyId,
      fuelUnit,
      entityId,
    });
  },
  async fetchDailyData({
    year,
    month,
    week,
    start = undefined,
    end = undefined,
    mode = undefined,
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    month: number;
    week?: number;
    start?: number;
    end?: number;
    mode?: string;
    activityTypeId?: string;
    fuelUnit?: fuelUnitType;
    entityId?: string;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await TimeSeriesDataRepository.fetchDailyData({
      year,
      month,
      week,
      start,
      end,
      mode,
      activityTypeId,
      companyId: selectedCompanyId,
      fuelUnit,
      entityId,
    });
  },
  async fetchMonthlyData({
    year,
    start = undefined,
    end = undefined,
    mode = undefined,
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    start?: number;
    end?: number;
    mode?: string;
    activityTypeId?: string;
    fuelUnit?: fuelUnitType;
    entityId?: string;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await TimeSeriesDataRepository.fetchMonthlyData({
      year,
      start,
      end,
      mode,
      activityTypeId,
      companyId: selectedCompanyId,
      fuelUnit,
      entityId,
    });
  },
  async fetchYearlyData({
    start = undefined,
    end = undefined,
    mode = undefined,
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    start?: number;
    end?: number;
    mode?: string;
    activityTypeId?: string;
    fuelUnit?: fuelUnitType;
    entityId?: string;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await TimeSeriesDataRepository.fetchYearlyData({
      start,
      end,
      mode,
      activityTypeId,
      companyId: selectedCompanyId,
      fuelUnit,
      entityId,
    });
  },
  async createElectricityTimeseriesData({
    year,
    month,
    date,
    hour,
    minute,
    deviceId,
    electricalValue,
    electricalPrice,
  }: {
    year: number;
    month: number;
    date: number;
    hour: number;
    minute: number;
    deviceId: string;
    electricalValue: number;
    electricalPrice: number;
  }) {
    return await TimeSeriesDataRepository.createTimeSeriesData({
      year,
      month,
      date,
      hour,
      minute,
      deviceId,
      electricalValue,
      electricalPrice,
    });
  },
  async createFuelTimeseriesData({
    year,
    month,
    date,
    hour,
    minute,
    deviceId,
    fuelValue,
    fuelPrice,
  }: {
    year: number;
    month: number;
    date: number;
    hour: number;
    minute: number;
    deviceId: string;
    fuelValue: number;
    fuelPrice: number;
  }) {
    return await TimeSeriesDataRepository.createTimeSeriesData({
      year,
      month,
      date,
      hour,
      minute,
      deviceId,
      fuelValue,
      fuelPrice,
    });
  },
  async createWaterTimeseriesData({
    year,
    month,
    date,
    hour,
    minute,
    deviceId,
    waterValue,
    waterPrice,
  }: {
    year: number;
    month: number;
    date: number;
    hour: number;
    minute: number;
    deviceId: string;
    waterValue: number;
    waterPrice: number;
  }) {
    return await TimeSeriesDataRepository.createTimeSeriesData({
      year,
      month,
      date,
      hour,
      minute,
      deviceId,
      waterValue,
      waterPrice,
    });
  },
  async createCo2TimeseriesData({
    year,
    month,
    date,
    hour,
    minute,
    deviceId,
    co2Value,
    co2Price,
  }: {
    year: number;
    month: number;
    date: number;
    hour: number;
    minute: number;
    deviceId: string;
    co2Value: number;
    co2Price: number;
  }) {
    return await TimeSeriesDataRepository.createTimeSeriesData({
      year,
      month,
      date,
      hour,
      minute,
      deviceId,
      co2Value,
      co2Price,
    });
  },
  async fetchMonthlyCostPrediction({
    year,
    month,
  }: {
    year: number;
    month: number;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await TimeSeriesDataRepository.fetchMonthlyCostPrediction({
      year,
      month,
      companyId: selectedCompanyId,
    });
  },
  async fetchYearlyCostPrediction({ year }: { year?: number }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    return await TimeSeriesDataRepository.fetchYearlyCostPrediction({
      year,
      companyId: selectedCompanyId,
    });
  },
};
