import IhiApiRepository from './IhiApiRepository';
import { toSnakeCase } from '@/utils/ToSnakeCase';
import {
  intensityTypeSchema,
  fuelAmountUnitSchema,
} from '@/zod-schemas/LiteralUnionSchema';
import { z } from 'zod';

const inputSchema = z.object({
  year: z.number().int(),
  month: z.number().int(),
  date: z.number().int().optional(),
  hour: z.number().int().optional(),
  minute: z.number().int().optional(),
  mode: intensityTypeSchema.optional(),
  start: z.number().int().optional(),
  end: z.number().int().optional(),
  week: z.number().int().optional(),
  activityTypeId: z.string().optional(),
  companyId: z.string().optional(),
  fuelUnit: fuelAmountUnitSchema.optional(),
});

export const graphKeySchema = z.enum([
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  '10',
  '11',
  '12',
  '13',
  '14',
  '15',
  '16',
]);

export const graphDataSchema = z.object({
  year: z.number().int(),
  month: z.number().int(),
  date: z.number().int(),
  hour: z.number().int().optional(),
  minute: z.number().int().optional(),
  //second: z.number().int().optional(), // 今のところAPIからは返されない
  electrical_value: z.number(),
  electrical_price: z.number(),
  co2_value: z.number(),
  co2_price: z.number(), //カーボンクレジット量ではないので注意
  electrical_value_reduction: z.number(), // 電力削減量
  electrical_price_reduction: z.number(), // 光熱削減費
  co2_value_reduction: z.number(), // CO2削減量
  co2_price_reduction: z.number(), // カーボンクレジット量
});

const responseSchema = z.record(graphKeySchema, graphDataSchema.array());

export type InputType = z.infer<typeof inputSchema>;
export type ResponseType = z.infer<typeof responseSchema>;

export default {
  async fetchGraphHoursData(input: InputType): Promise<ResponseType> {
    const { data } = await IhiApiRepository.get('graph_data/hours', {
      params: toSnakeCase(inputSchema.parse(input)),
    });
    return responseSchema.parse(data);
  },
  async fetchGraphDatesData(input: InputType): Promise<ResponseType> {
    const { data } = await IhiApiRepository.get('graph_data/dates', {
      params: toSnakeCase(inputSchema.parse(input)),
    });
    return responseSchema.parse(data);
  },
  async fetchGraphMinutesData(input: InputType): Promise<ResponseType> {
    const { data } = await IhiApiRepository.get('graph_data/minutes', {
      params: toSnakeCase(inputSchema.parse(input)),
    });
    return responseSchema.parse(data);
  },
};
