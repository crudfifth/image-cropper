<template>
  <table class="text-xs table-auto text-center border-b-2 min-w-full">
    <thead class="bg-neutral-200">
      <tr class="[&>th]:p-1">
        <th>
          <input
            v-model="isAllChecked"
            type="checkbox"
            class="form-checkbox h-5 w-5 text-gray-600"
            @change="toggleAll"
          />
        </th>
        <th>#</th>
        <th>チャンネル名（グラフ内訳）</th>
        <th>{{ `${valueTitle} ${unit}` }}</th>
        <!-- <th>2軸</th> -->
      </tr>
    </thead>
    <tbody class="divide-y [&>td]:p-1 text-sm">
      <tr
        v-for="(channel, idx) in channels"
        :key="channel.id"
        class="text-gray-700"
      >
        <td>
          <input
            :id="'checkbox-all-' + channel.id"
            :checked="modelValue[idx]"
            :disabled="!channel.isEnabled"
            type="checkbox"
            class="form-checkbox h-5 w-5 text-gray-600"
            @change="handleChange(idx, $event)"
          />
        </td>
        <td class="py-2 px-1">
          <div>
            <label :for="'checkbox-' + channel.id" class="text-sm leading-5">
              {{ channel.id }}
            </label>
          </div>
        </td>
        <td class="py-2 px-1 text-left">{{ channel.name }}</td>
        <td class="py-2 px-1">
          {{
            valueRoundFunction(normalizeZero(channel.value)).toLocaleString()
          }}
        </td>
        <!-- <td class="px-4 py-2">
          <input
            :id="'checkbox-2axes-' + channel.id"
            type="checkbox"
            class="form-checkbox h-5 w-5 text-gray-600"
          />
        </td> -->
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { GraphTableValueType } from './ChannelListSectionLayout.vue';

const props = defineProps<{
  channels: GraphTableValueType[];
  unit: string;
  valueTitle: string;
  valueRoundFunction: (value: number) => number;
  modelValue: boolean[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean[]): void;
}>();

const isAllChecked = computed(() => {
  const enabledChannels = props.modelValue.filter(
    (_, i) => props.channels[i].isEnabled
  );
  if (enabledChannels.length === 0) {
    return false;
  }
  return enabledChannels.every((value) => value);
});

const handleChange = (index: number, event: Event) => {
  const checked = (event.target as HTMLInputElement).checked;
  const updatedValues = [...props.modelValue];
  updatedValues[index] = checked;
  emit('update:modelValue', updatedValues);
};

const toggleAll = () => {
  emit(
    'update:modelValue',
    props.channels.map((channel) => channel.isEnabled && !isAllChecked.value)
  );
};

const normalizeZero = (value: number) => {
  // -0が表示されないようにする
  return value === 0 ? 0 : value;
};
</script>
