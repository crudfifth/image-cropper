import UserCountRepository from "@/repositories/UserCountRepository";

export default {
  async fetchRegisteredUserCount() {
    return await UserCountRepository.fetchRegisteredUserCount();
  }
};
