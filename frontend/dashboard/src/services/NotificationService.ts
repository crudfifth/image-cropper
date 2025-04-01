import NotificationRepository, {
  Notification,
  PaginationItems,
} from '../repositories/NotificationRepository';

export default {
  async fetchNotifications(
    { page, pageSize } = { page: 1, pageSize: 10 }
  ): Promise<PaginationItems<Notification>> {
    return await NotificationRepository.fetchNotifications({
      page,
      pageSize,
    });
  },
  async fethNotification(id: number): Promise<Notification> {
    return await NotificationRepository.fetchNotification(id);
  },
};
