// TODO: 廃止予定
import { intensityTypeSchema } from '@/zod-schemas/LiteralUnionSchema';
import { toSnakeCase } from '@/utils/ToSnakeCase';
import IhiApiRepository from './IhiApiRepository';
import { z } from 'zod';

const inputSchema = z.object({
  year: z.number().int(),
  month: z.number().int(),
  mode: intensityTypeSchema.optional(),
  start: z.number().int().optional(),
  end: z.number().int().optional(),
  intensityType: intensityTypeSchema.optional(),
  week: z.number().int().optional(),
  companyId: z.string().optional(),
});

export const responseSchema = z
  .object({
    year: z.number().int(),
    month: z.number().int(),
    date: z.number().int(),
    electrical_value: z.number(),
    electrical_price: z.number(),
    co2_value: z.number(),
    co2_price: z.number(),
  })
  .array();

export type InputType = z.infer<typeof inputSchema>;
export type ResponseType = z.infer<typeof responseSchema>;

export default {
  async fetchGraphDataReductions(input: InputType): Promise<ResponseType> {
    const { data } = await IhiApiRepository.get('graph_data_date_reduction/', {
      params: toSnakeCase(inputSchema.parse(input)),
    });
    return responseSchema.parse(data);
  },
};
