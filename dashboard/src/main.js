import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import { library } from '@fortawesome/fontawesome-svg-core';
import { faLeaf } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

library.add(faLeaf);
// Vue.component('font-awesome-icon', FontAwesomeIcon)

import './css/style.css';

import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { enableMock } from './mocks/api';

if (import.meta.env.VITE_API_MOCK) {
  enableMock();
}

const app = createApp(App);
app.use(router);
app.component('Fa', FontAwesomeIcon);
app.component('VueDatePicker', VueDatePicker);

app.mount('#app');
