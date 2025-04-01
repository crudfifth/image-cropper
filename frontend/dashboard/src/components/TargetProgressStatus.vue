<template>
  <div>
    <p
      v-if="progressPercentage && progressPercentage >= 80"
      class="text-center text-2xl mb-5"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 576 512"
        class="w-5 h-5 inline mr-3 mb-1"
        fill="currentColor"
      >
        <path
          d="M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"
        />
      </svg>
      <span v-if="progressPercentage < 100">今月の目標値を超えそうです</span>
      <span v-else>今月の目標値を超えています</span>
    </p>
    <div class="">
      <figure v-if="!progressPercentage || progressPercentage < 80">
        <img src="../images/signal-green.png" alt="" class="m-auto" />
      </figure>
      <figure
        v-if="
          progressPercentage &&
          progressPercentage >= 80 &&
          progressPercentage < 100
        "
      >
        <img src="../images/signal-yellow.png" alt="" class="m-auto" />
      </figure>
      <figure v-if="progressPercentage && progressPercentage >= 100">
        <img src="../images/signal-red.png" alt="" class="m-auto" />
      </figure>
      <p class="text-3xl font-bold text-center mb-5">
        対目標<span class="text-5xl">{{ progressPercentage ?? ' - ' }}</span
        >%
      </p>
      <div class="text-center">
        <button
          class="mx-auto text-lg text-slate-600 bg-white py-2 px-6 border shadow-md rounded"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 448 512"
            class="w-5 h-5 inline mr-3 mb-1"
            fill="#FB2C78"
          >
            <path
              d="M190.5 66.9l22.2-22.2c9.4-9.4 24.6-9.4 33.9 0L441 239c9.4 9.4 9.4 24.6 0 33.9L246.6 467.3c-9.4 9.4-24.6 9.4-33.9 0l-22.2-22.2c-9.5-9.5-9.3-25 .4-34.3L311.4 296H24c-13.3 0-24-10.7-24-24v-32c0-13.3 10.7-24 24-24h287.4L190.9 101.2c-9.8-9.3-10-24.8-.4-34.3z"
            />
          </svg>
          解決事例集はこちら
        </button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps({
  progressPercentage: {
    type: Number,
    required: true,
  },
});
</script>
