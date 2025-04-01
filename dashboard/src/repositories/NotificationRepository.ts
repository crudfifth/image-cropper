import IhiApiRepository from './IhiApiRepository';

export type Notification = {
  id: number;
  user: string;
  title: string;
  body: string;
  created_at: string;
  updated_at: string;
};

export type PaginationItems<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export default {
  async fetchNotifications(
    { page, pageSize } = { page: 1, pageSize: 10 }
  ): Promise<PaginationItems<Notification>> {
    const { data } = await IhiApiRepository.get('notifications/', {
      params: {
        page: page,
        page_size: pageSize,
      },
    });
    return data;
  },
  async fetchNotification(id: number): Promise<Notification> {
    const { data } = await IhiApiRepository.get(`notifications/${id}/`);
    return data;
  },
};
