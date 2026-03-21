const trimTrailingSlash = (value: string) => value.replace(/\/+$/, "");

const API_BASE_RAW = (import.meta.env.VITE_API_BASE_URL as string) || "";
const API_BASE = API_BASE_RAW ? trimTrailingSlash(API_BASE_RAW) : "";

const isLocalUrl = (value: string) => /^https?:\/\/(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?(\/|$)/i.test(value);

const isRemoteBrowserClient = () => {
  if (typeof window === "undefined") return false;
  return !["localhost", "127.0.0.1", "0.0.0.0"].includes(window.location.hostname);
};

export const resolveApiBaseUrl = (specificUrl: string | undefined, apiPath: string) => {
  if (specificUrl && specificUrl.length > 0) {
    // When accessed remotely (e.g. via zrok on a phone), ignore localhost-specific
    // service URLs and prefer the public API base if provided.
    if (API_BASE && isRemoteBrowserClient() && isLocalUrl(specificUrl)) {
      return `${API_BASE}${apiPath}`;
    }
    return trimTrailingSlash(specificUrl);
  }
  if (API_BASE) {
    return `${API_BASE}${apiPath}`;
  }
  return `http://localhost:8010${apiPath}`;
};

export const resolveMediaBaseUrl = (specificUrl: string | undefined) => {
  if (specificUrl && specificUrl.length > 0) {
    if (API_BASE && isRemoteBrowserClient() && isLocalUrl(specificUrl)) {
      return API_BASE;
    }
    return trimTrailingSlash(specificUrl);
  }
  if (API_BASE) {
    return API_BASE;
  }
  return "http://localhost:8010";
};
