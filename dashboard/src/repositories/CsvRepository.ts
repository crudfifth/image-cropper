import IhiApiRepository from '@/repositories/IhiApiRepository';
import UserRepository from './UserRepository';
import { openAlertModal } from '@/stores/AlertModalStore';
import { Company } from '@/types';
import { cloneDeep } from 'lodash-es';

export type CsvUploadHistory = {
  id: string;
  company: Company;
  file_name: string;
  size_bytes: number;
  uploaded_at: string;
};

export default {
  async fetchCsv(input: { startDate: Date; endDate: Date }): Promise<void> {
    try {
      // TBD: JSTを渡さないとAPIが正常に動作しないっぽいので、ワークアラウンドとして9時間進める。
      const startDate = cloneDeep(input.startDate);
      startDate.setHours(startDate.getHours() + 9);

      const endDate = cloneDeep(input.endDate);
      endDate.setHours(endDate.getHours() + 9);

      const companyId = await UserRepository.getSelectedCompanyId();
      const response = await IhiApiRepository({
        url: `companies/${companyId}/minute-data/csv/`,
        method: 'GET',
        responseType: 'blob',
        params: {
          start_datetime: startDate.toISOString().slice(0, -5), // APIがミリ秒入りのISO表記を受け付けないため、ミリ秒を削除
          end_datetime: endDate.toISOString().slice(0, -5),
        },
      });

      const fileName = 'minute-data.csv';
      const url = window.URL.createObjectURL(new Blob([response.data]));

      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch (err) {
      openAlertModal({
        body: 'CSVのダウンロードに失敗しました',
      });
    }
  },
  async uploadCsv(file: File): Promise<void> {
    try {
      const companyId = await UserRepository.getSelectedCompanyId();
      const formData = new FormData();
      formData.append('file', file);

      await IhiApiRepository({
        url: `companies/${companyId}/upload-csv/`,
        method: 'POST',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      openAlertModal({ body: 'CSVデータをアップロードしました' });
    } catch (err) {
      openAlertModal({
        body: 'CSVのアップロードに失敗しました',
      });
    }
  },
  async fetchUploadCsvHistory(): Promise<CsvUploadHistory[]> {
    try {
      const companyId = await UserRepository.getSelectedCompanyId();
      const response = await IhiApiRepository({
        url: `companies/${companyId}/csv-upload-histories/`,
        method: 'GET',
      });

      return response.data;
    } catch (err) {
      openAlertModal({
        body: 'CSVのアップロード履歴の取得に失敗しました',
      });
      return [];
    }
  },
};
