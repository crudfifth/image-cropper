import MockAdapter from 'axios-mock-adapter';
const validUUID = '123e4567-e89b-12d3-a456-426614174000';
// フロントエンドのテスト用URL: http://localhost:5173/signup-with-magic-link/?token=123e4567-e89b-12d3-a456-426614174000

export const mockMagicLinkTokenRepository = (axiosMock: MockAdapter) => {
  axiosMock.onGet('user-by-activation-token/').reply((config) => {
    const token = config.headers?.['User-Activation-Token'];
    if (token === validUUID) {
      return [
        200,
        {
          email: 'test@example.com',
        },
      ];
    } else {
      return [
        401,
        {
          message: 'Unauthorized',
        },
      ];
    }
  });
  axiosMock.onPost('/activate-user/').reply((config) => {
    const token = config.headers?.['User-Activation-Token'];
    const data = JSON.parse(config.data || '{}');
    if (
      token === validUUID &&
      data.username &&
      data.affiliation &&
      data.password
    ) {
      return [
        200,
        {
          message: 'ユーザーが正常にアクティブ化されました',
        },
      ];
    } else if (token !== validUUID) {
      return [
        401,
        {
          message: '認証に失敗しました',
        },
      ];
    } else {
      return [
        400,
        {
          message: '不正なリクエストです',
        },
      ];
    }
  });
};
