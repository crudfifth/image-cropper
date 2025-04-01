<template>
  <div class="relative">
    <NonNegativeNumberInput
      :model-value="modelValue"
      @update:model-value="handleInput"
      class="form-input rounded-md text-gray-700 pl-3 w-[125px]"
      :class="inputClasses"
      :disabled="isDisabled || additionalDisabledCondition"
    />
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="absolute rounded-r-md top-0 right-0 w-8 pr-6 h-full cursor-pointer"
      :class="selectClasses"
      :disabled="isDisabled || additionalDisabledCondition"
    >
      <option
        v-for="option in options"
        :key="option.id"
        :value="option.value"
      >{{ option.region_name ? `[${option.region_name}] ` : '' }}{{ option.text }}</option>
    </select>
    <div class="pointer-events-none absolute top-0 right-0 h-full flex items-center justify-center w-10">
      <svg :class="svgClasses" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="20" height="20">
        <path d="M6 8l4 4 4-4" stroke-width="2" fill="none" fill-rule="evenodd"/>
      </svg>
    </div>
  </div>
</template>

<script>
import NonNegativeNumberInput from './NonNegativeNumberInput.vue';

export default {
  components: {
    NonNegativeNumberInput
  },
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    options: {
      type: Array,
      default: () => []
    },
    isDisabled: {
      type: Boolean,
      default: false
    },
    additionalDisabledCondition: {
      type: Boolean,
      default: false,
    },
    dirtyField: {
      type: Function,
      default: null,
    }
  },
  computed: {
    inputClasses() {
      return {
        'cursor-not-allowed': this.isDisabled || this.additionalDisabledCondition,
        'bg-gray-200': this.isDisabled || this.additionalDisabledCondition,
        'text-gray-400': this.isDisabled || this.additionalDisabledCondition,
      };
    },
    selectClasses() {
      return {
        'cursor-not-allowed': this.isDisabled || this.additionalDisabledCondition,
        'opacity-30': this.isDisabled || this.additionalDisabledCondition,
        'border': true,
        'border-gray-300': !this.isDisabled && !this.additionalDisabledCondition,
        'border-opacity-50': !this.isDisabled && !this.additionalDisabledCondition,
      };
    },
    svgClasses() {
      return {
        'fill-current': true,
        'text-gray-400': this.isDisabled || this.additionalDisabledCondition,
      };
    }
  },
  methods: {
    handleInput(newValue) {
      this.$emit('update:modelValue', newValue); 
      this.validateChannels();
    },
    validateChannels() {
      if (this.dirtyField && typeof this.dirtyField === 'function') {
        this.$emit('validateChannels', this.dirtyField());
      }
    }
  }
}
</script>
