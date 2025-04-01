import IhiApiRepository from './IhiApiRepository';
import type { FuelAmountUnitType } from '@/types';

export type MonthlyData = {
  co2_price: number;
  co2_value: number;
  electrical_price: number;
  electrical_value: number;
  energy_saving_value: number;
  fuel_price: number;
  fuel_value: number;
  get_data_date: string;
  month: number;
  water_price: number;
  water_value: number;
};

export default {
  async fetchHourlyData({
    year,
    month,
    date,
    mode = undefined,
    activityTypeId = undefined,
    companyId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    month: number;
    date: number;
    mode?: string;
    activityTypeId?: string;
    companyId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }) {
    const { data } = await IhiApiRepository.get('data/hours', {
      params: {
        year,
        month,
        date,
        mode,
        activity_id: activityTypeId,
        company_id: companyId,
        fuel_unit: fuelUnit,
        entity_id: entityId,
      },
    });
    return data;
  },

  async fetchDailyData({
    year,
    month,
    week = undefined,
    start = undefined,
    end = undefined,
    mode = undefined,
    activityTypeId = undefined,
    companyId = undefined,
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
    companyId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }) {
    const { data } = await IhiApiRepository.get('data/dates', {
      params: {
        year,
        month,
        week,
        mode,
        start,
        end,
        activity_id: activityTypeId,
        company_id: companyId,
        fuel_unit: fuelUnit,
        entity_id: entityId,
      },
    });
    return data;
  },

  async fetchMonthlyData({
    year,
    start = undefined,
    end = undefined,
    mode = undefined,
    activityTypeId = undefined,
    companyId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    start?: number;
    end?: number;
    mode?: string;
    activityTypeId?: string;
    companyId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }): Promise<MonthlyData[]> {
    const { data } = await IhiApiRepository.get('data/months', {
      params: {
        year,
        start,
        end,
        mode,
        activity_id: activityTypeId,
        company_id: companyId,
        fuel_unit: fuelUnit,
        entity_id: entityId,
      },
    });
    return data;
  },

  async fetchYearlyData({
    start = undefined,
    end = undefined,
    mode = undefined,
    activityTypeId = undefined,
    companyId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    start?: number;
    end?: number;
    mode?: string;
    activityTypeId?: string;
    companyId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }) {
    const { data } = await IhiApiRepository.get('data/years', {
      params: {
        start,
        end,
        mode,
        activity_id: activityTypeId,
        company_id: companyId,
        fuel_unit: fuelUnit,
        entity_id: entityId,
      },
    });
    return data;
  },

  // データを手入力するためのAPI
  // TODO: デモ画面だけで使われていたっぽい。削除してもいいかも。
  async createTimeSeriesData({
    year,
    month,
    date,
    hour,
    minute,
    deviceId,
    electricalValue = 0,
    electricalPrice = 0,
    waterValue = 0,
    waterPrice = 0,
    fuelValue = 0,
    fuelPrice = 0,
    co2Value = 0,
    co2Price = 0,
    utilityCosts = 0,
  }: {
    year: number;
    month: number;
    date: number;
    hour: number;
    minute: number;
    deviceId: string;
    electricalValue?: number;
    electricalPrice?: number;
    waterValue?: number;
    waterPrice?: number;
    fuelValue?: number;
    fuelPrice?: number;
    co2Value?: number;
    co2Price?: number;
    utilityCosts?: number;
  }) {
    const { data } = await IhiApiRepository.post('data/', {
      year,
      month,
      date,
      hour,
      minute,
      electrical_value: electricalValue,
      electrical_price: electricalPrice,
      water_value: waterValue,
      water_price: waterPrice,
      fuel_value: fuelValue,
      fuel_price: fuelPrice,
      co2Value: co2Value,
      co2_price: co2Price,
      utility_costs: utilityCosts,
      device_id: deviceId,
    });
    return data;
  },

  async fetchMonthlyCostPrediction({
    year,
    month,
    companyId = undefined,
  }: {
    year?: number;
    month?: number;
    companyId?: string;
  }) {
    const { data } = await IhiApiRepository.get('data/predictions/monthly', {
      params: {
        year,
        month,
        company_id: companyId,
      },
    });
    return data;
  },

  async fetchYearlyCostPrediction({
    year,
    companyId = undefined,
  }: {
    year?: number;
    companyId?: string;
  }) {
    const { data } = await IhiApiRepository.get('data/predictions/yearly', {
      params: {
        year,
        company_id: companyId,
      },
    });
    return data;
  },
};
