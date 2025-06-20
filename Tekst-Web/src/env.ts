class Environment {
  WEB_PATH: string;
  STATIC_PATH: string;
  TEKST_API_PATH: string;

  constructor() {
    const baseHref = document.querySelector('base')?.href;
    this.WEB_PATH = baseHref ? new URL(baseHref).pathname : import.meta.env.BASE_URL || '/';
    const webPathStripped = this.WEB_PATH.replace(/\/+$/, '');
    this.STATIC_PATH = webPathStripped + '/static';
    // construct API path: If the API path is set via an env var, it's assumed to
    // contain the COMPLETE path to the API (including the web path
    // or any other path prefix).
    // If not, we assume that we're running the official container image and
    // the API is located under the web path.
    this.TEKST_API_PATH = import.meta.env.TEKST_API_PATH || webPathStripped + '/api';
  }
}

const env = new Environment();
export default env;
