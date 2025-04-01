import IhiApiRepository from '@/repositories/IhiApiRepository';
import { Entity, Structure, UserEntityPermission } from '@/types';

export default {
  async fetchStructures(companyId: string): Promise<Structure[]> {
    const { data } = await IhiApiRepository.get(
      `companies/${companyId}/data_structures/`
    );
    return data;
  },
  async fetchEntityList(
    companyId: string,
    onlyLeafNodes?: boolean
  ): Promise<Entity[]> {
    const { data } = await IhiApiRepository.get(
      `companies/${companyId}/entities/`,
      {
        params: {
          only_leaf_nodes: onlyLeafNodes ? 'true' : undefined,
        },
      }
    );
    return data;
  },
  async createEntity(
    companyId: string,
    name: string,
    parentEntityId: string
  ): Promise<Entity> {
    const { data } = await IhiApiRepository.post(
      `companies/${companyId}/entities/`,
      {
        name,
        parent_entity_id: parentEntityId,
      }
    );
    return data;
  },
  async deleteEntity(companyId: string, entityId: string): Promise<void> {
    await IhiApiRepository.delete(
      `companies/${companyId}/entities/${entityId}/`
    );
  },
  async fetchUserEntityPermissions(
    companyId: string,
    entityId: string
  ): Promise<UserEntityPermission[]> {
    const { data } = await IhiApiRepository.get(
      `companies/${companyId}/user_entity_permissions/`,
      {
        params: {
          entity_id: entityId,
        },
      }
    );
    return data;
  },
  async deleteUserEntityPermission(
    companyId: string,
    userEntityPermissionId: string
  ): Promise<void> {
    await IhiApiRepository.delete(
      `companies/${companyId}/user_entity_permissions/${userEntityPermissionId}/`
    );
  },
  async createUserEntityPermission(
    companyId: string,
    userId: string,
    entityId: string
  ): Promise<UserEntityPermission> {
    const { data } = await IhiApiRepository.post(
      `companies/${companyId}/user_entity_permissions/`,
      {
        user_id: userId,
        entity_id: entityId,
      }
    );
    return data;
  },
};
