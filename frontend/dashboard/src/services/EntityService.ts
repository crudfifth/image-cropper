import EntityRepository from '@/repositories/EntityRepository';
import UserRepository from '@/repositories/UserRepository';
import type { Entity, Structure, EntityStructure } from '@/types';
import { MAX_ENTITY_STRUCTURE_DEPTH } from '@/constants';

type EntityStructureToRecursive = {
  entity: Entity;
  children: EntityStructureToRecursive[];
  structures: Structure[];
};

// サーバからClosure Tableの構造がそのまま返ってくるため、ネストしたオブジェクトに変換する
// Closure Tableのの概要はSQLアンチパターン第2章またはそれを説明したWeb記事を参照のこと
const makeEntityStructureRecursive = (
  entity: Entity,
  depth: number,
  structures: Structure[]
): EntityStructureToRecursive => {
  if (depth > MAX_ENTITY_STRUCTURE_DEPTH) {
    return { entity, children: [], structures };
  }
  const children = structures
    .filter((structure) => structure.ancestor.id === entity.id)
    .map((structure) =>
      makeEntityStructureRecursive(structure.descendant, depth + 1, structures)
    );

  return { entity, children, structures };
};

const defaultEntityStructure: {
  entitiesFlat: Entity[];
  entitiesStructure: EntityStructure;
} = {
  entitiesFlat: [],
  entitiesStructure: {
    entity: {
      id: '',
      name: '',
      company: '',
    },
    children: [],
  },
};

export default {
  // エンティティの構造を取得する。
  // エンティティの構造をネストしたオブジェクトで返す。
  async fetchEntityStructure() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return defaultEntityStructure;
    }
    const structures = await EntityRepository.fetchStructures(
      selectedCompanyId
    );

    const root = structures.find((structure) => structure.is_root);

    const entities = structures
      .filter((s) => s.depth === 0)
      .map((s) => s.ancestor);
    const directChildrenStructure = structures.filter((s) => s.depth === 1);

    if (!root) {
      return defaultEntityStructure;
    }

    const entityStructure = makeEntityStructureRecursive(
      root?.ancestor,
      1,
      directChildrenStructure
    );
    return {
      entitiesFlat: entities,
      entitiesStructure: {
        entity: entityStructure.entity,
        children: entityStructure.children,
      },
    };
  },
  // エンティティのリストを取得する。
  // Closure Tableの構造をそのまま返す。
  async fetchStructures() {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return [];
    }
    return await EntityRepository.fetchStructures(selectedCompanyId);
  },
  // エンティティのリストを取得する。
  async fetchEntityList({
    onlyLeafNodes = false,
  }: {
    onlyLeafNodes?: boolean;
  }) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return [];
    }
    return await EntityRepository.fetchEntityList(
      selectedCompanyId,
      onlyLeafNodes
    );
  },
  async createEntity(name: string, parentEntityId: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return null;
    }
    return await EntityRepository.createEntity(
      selectedCompanyId,
      name,
      parentEntityId
    );
  },
  async deleteEntity(entityId: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return null;
    }
    return await EntityRepository.deleteEntity(selectedCompanyId, entityId);
  },
  async fetchUserEntityPermissions(entityId: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return [];
    }
    return await EntityRepository.fetchUserEntityPermissions(
      selectedCompanyId,
      entityId
    );
  },
  async deleteUserEntityPermission(userEntityPermissionId: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return null;
    }
    return await EntityRepository.deleteUserEntityPermission(
      selectedCompanyId,
      userEntityPermissionId
    );
  },
  async createUserEntityPermission(userId: string, entityId: string) {
    const selectedCompanyId = await UserRepository.getSelectedCompanyId();
    if (!selectedCompanyId) {
      return null;
    }
    return await EntityRepository.createUserEntityPermission(
      selectedCompanyId,
      userId,
      entityId
    );
  },
};
