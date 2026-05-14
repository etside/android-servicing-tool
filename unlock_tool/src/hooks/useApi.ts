import { useQuery, type UseQueryOptions } from "@tanstack/react-query";

const fetcher = async <T>(path: string): Promise<T> => {
  const url = path.startsWith("/api") ? path : `/api${path}`;
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  return res.json() as Promise<T>;
};

export function useApi<T = unknown>(
  path: string,
  options?: Omit<UseQueryOptions<T, Error>, "queryKey" | "queryFn">
) {
  return useQuery<T, Error>({
    queryKey: ["api", path],
    queryFn: () => fetcher<T>(path),
    ...options,
  });
}
