import axios from 'axios';
import { z } from 'zod';
import { FailableResponseType } from '@/types';

const baseURL = `${
  import.meta.env.VITE_APP_API_URL ?? 'https://ihi-backend.bizfreak.co.jp:2343'
}/api/v1`;

export const axiosInstance = axios.create({
  baseURL,
});

const activateUserInputSchema = z.object({
  magicLinkToken: z.string().uuid(),
  userName: z.string(),
  affiliation: z.string(),
  password: z.string(),
});

export type activateUserInputType = z.infer<typeof activateUserInputSchema>;

const fetchUserInputSchema = z.object({
  magicLinkToken: z.string().uuid(),
});

export type fetchUserInputType = z.infer<typeof fetchUserInputSchema>;

const fetchUserOutputSchema = z.object({
  email: z.string(),
});

export type fetchUserOutputType = z.infer<typeof fetchUserOutputSchema>;

export default {
  fetchUserByActivationToken: async (
    input: fetchUserInputType
  ): Promise<FailableResponseType<fetchUserOutputType>> => {
    try {
      const response = await axiosInstance.get('user-by-activation-token/', {
        headers: {
          'User-Activation-Token': input.magicLinkToken,
        },
      });
      const validatedData = fetchUserOutputSchema.parse(response.data);
      return { success: true, data: validatedData };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          return {
            success: false,
            status: error.response.status,
            error: '認証に失敗しました。招待を受け直して下さい。',
            details: error.response.data,
          };
        }
      }
      throw new Error(`予期せぬエラーが発生しました: ${error}`);
    }
  },
  activateUser: async (
    input: activateUserInputType
  ): Promise<FailableResponseType<any>> => {
    try {
      const response = await axiosInstance.post(
        '/activate-user/',
        {
          username: input.userName,
          affiliation: input.affiliation,
          password: input.password,
        },
        {
          headers: {
            'User-Activation-Token': input.magicLinkToken,
          },
        }
      );
      return { success: true, data: response.data };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 400) {
          return {
            success: false,
            status: error.response.status,
            error: '不正なリクエストです。',
            details: error.response.data,
          };
        } else if (error.response?.status === 401) {
          return {
            success: false,
            status: error.response.status,
            error: '認証に失敗しました。招待を受け直してください。',
            details: error.response.data,
          };
        }

        return {
          success: false,
          status: 500,
          error: 'ユーザーのアクティベーション中にエラーが発生しました。',
          details: error,
        };
      }

      throw new Error(`予期せぬエラーが発生しました: ${error}`);
    }
  },
};
