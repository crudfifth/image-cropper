import AuthTokenRepository from '../repositories/AuthTokenRepository';
import RememberMeRepository from '@/repositories/RememberMeRepository';
import IhiApiRepository from '../repositories/IhiApiRepository';
import { isRepositoryError } from '../repositories/RepositoryError';
import { User, default as UserRepsitory } from '../repositories/UserRepository';

export class InvalidTokenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidTokenError';
  }
}

export class InvalidPasswordError extends Error {
  errors: string[];

  constructor(message: string, errors: string[]) {
    super(message);
    this.name = 'InvalidPasswordError';
    this.errors = errors;
  }
}

export class UserConflictError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'UserConflictError';
  }
}

export default {
  async signup({
    username,
    email,
    password,
    affiliation,
    is_locked,
    company_id,
  }: {
    username: string;
    email: string;
    password?: string;
    affiliation?: string | null;
    is_locked?: boolean;
    company_id?: string;
  }) {
    try {
      return await UserRepsitory.create({
        username: username,
        email: email,
        password: password,
        affiliation: affiliation,
        is_locked: is_locked,
        company_id: company_id,
      });
    } catch (error) {
      if (isRepositoryError(error)) {
        if (error.response.status === 409) {
          throw new UserConflictError(error.response.data?.message ?? '');
        } else if (
          error.response.status === 400 &&
          error.response.data?.password
        ) {
          throw new InvalidPasswordError(
            'Bad request',
            error.response.data.password
          );
        }
      }
      throw error;
    }
  },
  async activate(activationToken: string) {
    const { data } = await UserRepsitory.activate(activationToken);
    return data;
  },
  async signIn({
    email,
    password,
    isRememberMe,
  }: {
    email: string;
    password: string;
    isRememberMe?: boolean;
  }) {
    const { data } = await IhiApiRepository.post('token/', {
      email: email,
      password: password,
    });
    if (isRememberMe !== undefined) {
      RememberMeRepository.saveRememberMe(isRememberMe);
    }
    AuthTokenRepository.saveToken(data.access, data.refresh);
    return data;
  },
  async signOut() {
    UserRepsitory.removeSelectedCompanyId();
    AuthTokenRepository.removeToken();
  },
  async requestResetPassword(email: string) {
    const { data } = await UserRepsitory.requestResetPassword(email);
    return data;
  },
  async resetPassword({
    token,
    password,
  }: {
    token: string;
    password: string;
  }) {
    try {
      const data = await UserRepsitory.resetPassword({ token, password });
      return data;
    } catch (error) {
      if (isRepositoryError(error)) {
        if (error.response.status === 404) {
          throw new InvalidTokenError('Invalid token');
        } else if (
          error.response.status === 400 &&
          error.response.data?.password
        ) {
          throw new InvalidPasswordError(
            'Bad request',
            error.response.data.password
          );
        }
      }
      throw error;
    }
  },
  async changePassword({
    current_password,
    new_password,
  }: {
    current_password: string;
    new_password: string;
  }) {
    const { data } = await UserRepsitory.changePassword({
      current_password,
      new_password,
    });
    return data;
  },
  async fetchCurrentUser(): Promise<User> {
    return await UserRepsitory.fetchCurrentUser();
  },
  async setPassword(
    password: string,
    uid: string,
    token: string
  ): Promise<User> {
    return await UserRepsitory.setPassword(password, uid, token);
  },
  async update(userId: string, params: Partial<User>): Promise<User> {
    return await UserRepsitory.update(userId, params);
  },
  async updateUser({
    userId,
    userName,
    userAffiliation,
  }: {
    userId: string;
    userName: string;
    userAffiliation?: string;
  }): Promise<User> {
    const updateUser = await UserRepsitory.update(userId, {
      username: userName,
      affiliation: userAffiliation || '',
    });
    return updateUser;
  },
  async updateUserName(userId: string, userName: string): Promise<User> {
    return await UserRepsitory.update(userId, { username: userName });
  },
  async agreeToTermsOfService(userId: string): Promise<User> {
    return await UserRepsitory.update(userId, {
      is_agreed_to_terms_of_service: true,
    });
  },
  setSelectedCompany(companyId: string) {
    UserRepsitory.setSelectedCompany(companyId);
  },
  async getSelectedCompanyId() {
    return await UserRepsitory.getSelectedCompanyId();
  },
  async fetchUsers() {
    const selectedCompanyId = await UserRepsitory.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return [];
    }
    return await UserRepsitory.fetchUsers(selectedCompanyId);
  },
  async fetchUsersByEmail(email: string) {
    const selectedCompanyId = await UserRepsitory.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return [];
    }
    return await UserRepsitory.fetchUsersByEmail(email, selectedCompanyId);
  },
  async deleteUser(userId: string) {
    return await UserRepsitory.deleteUser(userId);
  },
};
