import { Company } from '@/types';
import IhiApiRepository from './IhiApiRepository';
import CompanyService from '@/services/CompanyService';
import AsyncLock from 'async-lock';
import { openAlertModal } from '@/stores/AlertModalStore';

export type User = {
  id: string;
  username: string;
  email: string;
  is_staff: boolean;
  is_superuser: boolean;
  is_locked: boolean;
  has_manage_role: boolean;
  has_view_role: boolean;
  company_id: string | undefined;
  company: Company;
  is_agreed_to_terms_of_service: boolean;
  affiliation: string | null;
  is_manager: boolean;
  is_active: boolean;
};

let currentCompanyId: string | undefined = undefined;

const companyIdLockKey = 'companyIdLockKey';
const companyIdlock = new AsyncLock();

export default {
  async fetchUsers(company_id: string) {
    const { data } = await IhiApiRepository.get('users/', {
      params: {
        company_id: company_id,
      },
    });
    return data;
  },
  async fetchUsersByEmail(email: string, companyId: string) {
    const { data } = await IhiApiRepository.get('users/', {
      params: {
        email: email,
        company_id: companyId,
      },
    });
    return data;
  },
  async create(params: {
    username: string;
    email: string;
    password?: string;
    affiliation?: string | null;
    is_locked?: boolean;
    company_id?: string;
  }) {
    const { data } = await IhiApiRepository.post('users/', params);
    return data;
  },
  async activate(activationToken: string) {
    const { data } = await IhiApiRepository.post('users/activate/', {
      token: activationToken,
    });
    return data;
  },
  async requestResetPassword(email: string) {
    const { data } = await IhiApiRepository.post('password_reset/', {
      email: email,
    });
    return data;
  },
  async resetPassword({
    token,
    password,
  }: {
    token: string;
    password: string;
  }) {
    const { data } = await IhiApiRepository.post('password_reset/confirm/', {
      token: token,
      password: password,
    });
    return data;
  },
  async changePassword({
    current_password,
    new_password,
  }: {
    current_password: string;
    new_password: string;
  }) {
    const { data } = await IhiApiRepository.post('user/change_password/', {
      current_password: current_password,
      new_password: new_password,
    });
    return data;
  },
  async fetchCurrentUser(): Promise<User> {
    const { data } = await IhiApiRepository.get(`user/`);
    if (data.affiliation === null) {
      data.affiliation = '';
    }
    return data;
  },
  async setPassword(
    password: string,
    uid: string,
    token: string
  ): Promise<User> {
    const { data } = await IhiApiRepository.post(
      `user/reset_password/${uid}/${token}/`,
      {
        password,
      }
    );
    return data;
  },
  async update(userId: string, params: Partial<User>): Promise<User> {
    const { data } = await IhiApiRepository.patch(`users/${userId}`, params);
    return data;
  },
  setSelectedCompany(companyId: string) {
    // companyIdを保存する仕組みをlocalStorageに依存しないようにしたので、今は何もしない。
    // 依存しているコンポーネントが残っているのでそのままにしているが、今後削除する。
  },
  async getSelectedCompanyId() {
    return companyIdlock.acquire(companyIdLockKey, async () => {
      if (currentCompanyId) {
        return currentCompanyId;
      }

      const companies = await CompanyService.fetchCompanies();
      if (companies.length === 0) {
        openAlertModal({ body: '所属している企業がありません。' });
        return undefined;
      }

      currentCompanyId = companies[0].id;
      return currentCompanyId;
    });
  },
  removeSelectedCompanyId() {
    currentCompanyId = undefined;
  },
  async deleteUser(userId: string) {
    const { data } = await IhiApiRepository.delete(`users/${userId}`);
    return data;
  },
};
