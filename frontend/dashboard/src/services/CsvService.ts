import CsvRepository from '@/repositories/CsvRepository';

export default {
  async fetchCsv(input: { startDate: Date; endDate: Date }): Promise<void> {
    await CsvRepository.fetchCsv(input);
  },
  async uploadCsv(csvContent: string, fileName: string): Promise<void> {
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const file = new File([blob], fileName, {
      type: 'text/csv',
      lastModified: new Date().getTime(),
    });
    return await CsvRepository.uploadCsv(file);
  },
  async fetchCsvUploadHistories() {
    const historyList = await CsvRepository.fetchUploadCsvHistory();
    return historyList.map((history) => ({
      id: history.id,
      fileName: history.file_name,
      size: history.size_bytes,
      date: new Date(history.uploaded_at),
    }));
  },
};
