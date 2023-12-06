export function hashCode(obj: any) {
  const string = JSON.stringify(obj);
  let hash = 0;
  for (let i = 0; i < string.length; i++) {
    const code = string.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash;
  }
  return hash;
}
