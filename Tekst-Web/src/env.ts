class Environment {
  WEB_PATH: string;
  WEB_PATH_STRIPPED: string;
  STATIC_PATH: string;
  TEKST_API_PATH: string;

  constructor() {
    const baseHref = document.querySelector('base')?.href;
    this.WEB_PATH = baseHref ? new URL(baseHref).pathname : import.meta.env.BASE_URL || '/';
    this.WEB_PATH_STRIPPED = this.WEB_PATH.replace(/\/+$/, '');
    this.STATIC_PATH = this.WEB_PATH_STRIPPED + '/static';
    // construct API path: If the API path is set via an env var, it's assumed to
    // contain the COMPLETE path to the API (including the web path
    // or any other path prefix).
    // If not, we assume that we're running the official container image and
    // the API is located under the web path.
    this.TEKST_API_PATH = import.meta.env.TEKST_API_PATH || this.WEB_PATH_STRIPPED + '/api';
  }
}

const env = new Environment();
export default env;
