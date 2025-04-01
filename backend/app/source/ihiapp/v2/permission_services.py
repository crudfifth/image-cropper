from ..models import DataStructure, UserEntityPermission
from users.models import Company, User, CompanyUser


# ユーザ権限の確認
# 「管理」できるユーザの判定
def is_user_manager(company_id, user_id, group=None):
    """
    指定されたユーザーが、指定された企業で「管理」権限を持っているかどうかを判定する。

    この関数は、ユーザーが企業の管理者であるか、または管理権限を持つグループに属しているかどうかを確認します。
    ユーザーが企業のadmin_user_idとして登録されている場合、またはユーザーが「ユーザー管理者」または「管理権限」グループに属している場合に、管理権限があると判定されます。

    Parameters:
    - company_id (int): 管理権限を確認したい企業のID。
    - user_id (int): 管理権限の確認対象となるユーザーのID。
    - group (QuerySet, optional): ユーザーが属するグループのクエリセット。デフォルトはNone。

    Returns:
    - bool: ユーザーが指定された企業で管理権限を持っている場合はTrue、そうでない場合はFalse。
    """
    # ユーザ管理者
    if Company.objects.filter(id=company_id, admin_user_id=user_id).exists():
        return True
    # 企業に所属していて、管理権限を持っている
    if group and User.objects.filter(id=user_id, company_id_id=company_id).exists() or CompanyUser.objects.filter(user_id=user_id, company_id=company_id).exists():
        if group.filter(name__in=['ユーザー管理者', '管理権限']).exists():
            return True
    return False

def is_user_viewer(company_id, user_id, group=None):
    """
    指定されたユーザーが、指定された企業のデータを「閲覧」できるかどうかを判定する。

    この関数は、ユーザーが企業のデータを閲覧する権限を持っているかどうかを確認します。
    ユーザーが企業の管理者である場合、またはユーザーが企業に所属しており、
    「ユーザー管理者」、「管理権限」、または「閲覧権限」のいずれかのグループに属している場合に閲覧権限があると判定されます。

    Parameters:
    - company_id (int): 閲覧権限を確認したい企業のID。
    - user_id (int): 閲覧権限の確認対象となるユーザーのID。
    - group (QuerySet, optional): ユーザーが属するグループのクエリセット。デフォルトはNone。

    Returns:
    - bool: ユーザーが指定された企業のデータを閲覧する権限がある場合はTrue、そうでない場合はFalse。
    """
    # ユーザ管理者
    if Company.objects.filter(id=company_id, admin_user_id=user_id).exists():
        return True
    # 企業に所属していて、管理権限or閲覧権限を持っている
    if group and User.objects.filter(id=user_id, company_id_id=company_id).exists() or CompanyUser.objects.filter(user_id=user_id, company_id=company_id).exists():
        if group.filter(name__in=['ユーザー管理者', '管理権限', '閲覧権限']).exists():
            return True
    return False 

# 一般ユーザ
def is_user_normal(company_id, user_id):
    """
    指定されたユーザーが、指定された企業に一般ユーザーとして所属しているかどうかを判定する。

    この関数は、ユーザーが特定の企業に一般ユーザーとして所属しているかどうかを確認します。
    UserオブジェクトまたはCompanyUserオブジェクトを通じて、ユーザーが企業に所属しているかをチェックします。

    Parameters:
    - company_id (int): 所属を確認したい企業のID。
    - user_id (int): 所属の確認対象となるユーザーのID。

    Returns:
    - bool: ユーザーが指定された企業に一般ユーザーとして所属している場合はTrue、そうでない場合はFalse。
    """
    if User.objects.filter(id=user_id, company_id_id=company_id).exists() or CompanyUser.objects.filter(user_id=user_id, company_id=company_id).exists():
        return True
    return False 

def permitted_entity(company_id, user_id):
    """
    指定されたユーザーが、指定された企業に対してアクセス権を持つEntityかどうかを判定する。

    この関数は、ユーザーが特定の企業のEntityにアクセスする権限があるかどうかを確認します。
    管理者ユーザーは対象企業の全エンティティにアクセスできます。
    それ以外のユーザーは、UserEntityPermissionを通じて明示的にアクセス権が与えられたEntityのみアクセス可能です。

    Parameters:
    - company_id (int): アクセス権を確認したい企業のID。
    - user_id (int): アクセス権の確認対象となるユーザーのID。

    Returns:
    - bool: ユーザーが指定された企業のEntityにアクセスする権限がある場合はTrue、そうでない場合はFalse。
    """
    try:
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=user_id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id.id != user_id: # adminは対象企業の全エンティティを見られる
            root_entity = target_company.root_entity
            if root_entity is None or not root_entity.id in all_permit_entity_ids:
                return False
        return True
    except:
        return False
