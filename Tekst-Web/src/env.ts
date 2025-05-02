class Environment {
  WEB_PATH: string;
  STATIC_PATH: string;
  TEKST_API_PATH: string;

  constructor() {
    const baseHref = document.querySelector('base')?.href;
    this.WEB_PATH = baseHref ? new URL(baseHref).pathname : import.meta.env.BASE_URL || '/';
    this.STATIC_PATH = this.WEB_PATH.replace(/\/+$/, '') + '/static';
    this.TEKST_API_PATH = import.meta.env.TEKST_API_PATH || '/api';
  }
}

const env = new Environment();
export default env;
