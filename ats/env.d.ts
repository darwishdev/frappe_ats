/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// Frappe globals
declare global {
  interface Window {
    frappe: any;
    __: (text: string) => string;
    cur_frm: any;
    cur_list: any;
  }

  const frappe: any;
  const __: (text: string) => string;
}

export {};
