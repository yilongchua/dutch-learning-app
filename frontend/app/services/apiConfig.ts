const trimTrailingSlash = (value: string) => value.replace(/\/+$/, "");

const API_BASE_RAW = (import.meta.env.VITE_API_BASE_URL as string) || "";
const API_BASE = API_BASE_RAW ? trimTrailingSlash(API_BASE_RAW) : "";

export const resolveApiBaseUrl = (specificUrl: string | undefined, apiPath: string) => {
  if (specificUrl && specificUrl.length > 0) {
    return trimTrailingSlash(specificUrl);
  }
  if (API_BASE) {
    return `${API_BASE}${apiPath}`;
  }
  return `http://localhost:8010${apiPath}`;
};

export const resolveMediaBaseUrl = (specificUrl: string | undefined) => {
  if (specificUrl && specificUrl.length > 0) {
    return trimTrailingSlash(specificUrl);
  }
  if (API_BASE) {
    return API_BASE;
  }
  return "http://localhost:8010";
};
