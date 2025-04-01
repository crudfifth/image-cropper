import { z } from 'zod';

export const fuelAmountUnitSchema = z.enum(['yen', 'm3', 'L', 'kg']);

export const electricityAmountUnitSchema = z.enum(['yen', 'kWh']);

export const intensityTypeSchema = z.enum(['default', 'intensity']);

export const entitySelectionTypeSchema = z.enum(['whole', 'selectLayer']);

export const timePeriodTypeSchema = z.enum([
  'four-hour',
  'day',
  'week',
  'month',
  'year', // TODO: 廃止予定
]);

export const energyTypeSchema = z.enum(['utilityCost', 'electricity', 'co2']);

export const trendGraphTypeSchema = z.enum([
  'electricity',
  'utilityCost',
  'co2Emission',
  'carbonCredit',
  'electricityReduction',
  'utilityCostReduction',
  'co2EmissionReduction',
  'carbonFootprint',
]);

export const connectionStatusSchema = z.enum(['connected', 'disconnected']);
