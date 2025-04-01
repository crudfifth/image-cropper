import IhiApiRepository from './IhiApiRepository';
import type { FuelAmountUnitType } from '@/types';

export type BasicValueDataType = {
  electrical_value: number;
  electrical_price: number;
  water_value: number;
  water_price: number;
  fuel_value: number;
  fuel_price: number;
  co2_value: number;
  co2_price: number;
  get_data_date: string;
  entity_id: string;
  fuel_unit: FuelAmountUnitType;
};

export const BasicValueDataDefault: BasicValueDataType = {
  electrical_value: 0,
  electrical_price: 0,
  water_value: 0,
  water_price: 0,
  fuel_value: 0,
  fuel_price: 0,
  co2_value: 0,
  co2_price: 0,
  get_data_date: '',
  entity_id: '',
  fuel_unit: 'yen' as FuelAmountUnitType,
};

export type YearlyDataType = BasicValueDataType & { year: number };

export type MonthlyDataType = YearlyDataType & { month: number };

export type DailyDataType = MonthlyDataType & { date: number };

export type HourlyDataType = DailyDataType & { hour: number };

export default {
  async fetchHourlyData({
    year,
    month,
    date,
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    month: number;
    date: number;
    activityTypeId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }): Promise<HourlyDataType[]> {
    const { data } = await IhiApiRepository.get(`entities/${entityId}/hours`, {
      params: {
        year,
        month,
        date,
        activity_id: activityTypeId,
        fuel_unit: fuelUnit,
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
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    month: number;
    week?: number;
    start?: number;
    end?: number;
    activityTypeId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }): Promise<DailyDataType[]> {
    const { data } = await IhiApiRepository.get(`entities/${entityId}/dates`, {
      params: {
        year,
        month,
        week,
        start,
        end,
        activity_id: activityTypeId,
        fuel_unit: fuelUnit,
      },
    });
    return data;
  },

  async fetchMonthlyData({
    year,
    start = undefined,
    end = undefined,
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    year: number;
    start?: number;
    end?: number;
    activityTypeId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }): Promise<MonthlyDataType[]> {
    const { data } = await IhiApiRepository.get(`entities/${entityId}/months`, {
      params: {
        year,
        start,
        end,
        activity_id: activityTypeId,
        fuel_unit: fuelUnit,
      },
    });
    return data;
  },

  async fetchYearlyData({
    start = undefined,
    end = undefined,
    activityTypeId = undefined,
    fuelUnit = undefined,
    entityId = undefined,
  }: {
    start?: number;
    end?: number;
    activityTypeId?: string;
    fuelUnit?: FuelAmountUnitType;
    entityId?: string;
  }): Promise<YearlyDataType[]> {
    const { data } = await IhiApiRepository.get(`entities/${entityId}/years`, {
      params: {
        start,
        end,
        activity_id: activityTypeId,
        fuel_unit: fuelUnit,
      },
    });
    return data;
  },
};
