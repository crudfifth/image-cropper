<template>
  <div class="flex items-center">
    <label
      class="block uppercase tracking-wide text-gray-700 text-xs font-bold mr-3 whitespace-nowrap"
      for="grid-state"
    >
      期間起点
    </label>
    <div class="col-span-2">
      <VueDatePicker
        v-model="localvalue"
        :enable-time-picker="true"
        minutes-increment="10"
        minutes-grid-increment="10"
        :disabled-dates="(date) => date > new Date()"
        placeholder="日付を選択"
        locale="jp"
        :format="'yyyy年MM月dd日 HH:mm'"
        select-text="OK"
        time-picker-inline
        :clearable="false"
        cancel-text="キャンセル"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import VueDatePicker from '@vuepic/vue-datepicker';
const localvalue = defineModel<Date>();
</script>
