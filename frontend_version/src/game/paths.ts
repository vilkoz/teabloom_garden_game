const normalize = (value: string): string => value.replace(/^\/+/, '');

export function appUrl(path: string): string {
  return new URL(normalize(path), window.location.origin + import.meta.env.BASE_URL).toString();
}
