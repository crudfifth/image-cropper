import { AxiosError, isAxiosError } from 'axios';

export type RepositoryError = AxiosError & {
  response: {
    data?: {
      message: string;
      errors: string[];
      password: string[];
    };
  };
};

export const isRepositoryError = (error: any): error is RepositoryError => {
  return isAxiosError(error);
};
