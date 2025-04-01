<!-- 左側ドックパネル -->
<template>
  <div class="col-span-3">
    <div
      class="h-full flex flex-col col-span-4 text-white bg-main-blue shadow-lg rounded-md"
    >
      <div class="p-6">
        <section class="border-b pb-5">
          <AchievementSectionLayout />
        </section>

        <div class="pb-5">
          <section class="pb-5 py-5">
            <PredictionSectionLayout
              v-if="graphStateStore.graphType !== 'carbonFootprint'"
            />
            <CarbonFootprintSectionLayout v-else />
          </section>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import AchievementSectionLayout from './AchievementSectionLayout.vue';
import PredictionSectionLayout from './PredictionSectionLayout.vue';
import CarbonFootprintSectionLayout from './CarbonFootprintSectionLayout.vue';
import { graphStateStore } from '@/stores/TrendGraphStore';
</script>
