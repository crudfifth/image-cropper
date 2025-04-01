import { User } from '@/repositories/UserRepository';
import { z } from 'zod';
import * as schemas from '@/zod-schemas/LiteralUnionSchema';
import { AxiosError } from 'axios';

export type FailableResponseType<T> =
  | {
      success: true;
      data: T;
    }
  | {
      success: false;
      status: number;
      error: string;
      details: AxiosError;
    };

export type Structure = {
  id: string;
  ancestor: Entity;
  descendant: Entity;
  is_root: boolean;
  depth: number;
};

export type Entity = {
  id: string;
  name: string;
  company: string;
};

export type EntityStructure = {
  entity: Entity;
  children: EntityStructure[];
};

export type UserEntityPermission = {
  id: string;
  user: User;
  entity: Entity;
};

export type FuelAmountUnitType = z.infer<typeof schemas.fuelAmountUnitSchema>;

export type ElectricityAmountUnitType = z.infer<
  typeof schemas.electricityAmountUnitSchema
>;

export type IntensityType = z.infer<typeof schemas.intensityTypeSchema>;

export type EntitySelectionType = z.infer<
  typeof schemas.entitySelectionTypeSchema
>;

export type TimePeriodType = z.infer<typeof schemas.timePeriodTypeSchema>;

export type TrendGraphType = z.infer<typeof schemas.trendGraphTypeSchema>;

export type EnergyType = z.infer<typeof schemas.energyTypeSchema>;

export type ConnectionStatusType = z.infer<
  typeof schemas.connectionStatusSchema
>;

export type HistoryItem = {
  id: string;
  name: string;
  field: string;
  company: string;
  before: number;
  after: number;
  created_at: string;
};

export type UnitPrice = {
  co2_unit_price: number;
  electric_unit_co2: number;
  electric_unit_price: number;
  fuel_unit_co2: number;
  fuel_unit_price: number;
  water_unit_co2: number;
  water_unit_price: number;
};

export type Company = {
  id: string;
  name: string;
  economic_activity_unit: string;
  batch_enabled: boolean;
  created_at: string;
  updated_at: string;
};

export type IsCompanyAdmin = {
  is_admin: boolean;
};
