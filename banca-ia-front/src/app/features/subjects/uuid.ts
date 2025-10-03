export function v4(): string {
  const c = crypto.getRandomValues(new Uint8Array(16));
  c[6] = (c[6] & 0x0f) | 0x40; // version 4
  c[8] = (c[8] & 0x3f) | 0x80; // variant
  const toHex = (n: number) => n.toString(16).padStart(2, '0');
  const s = Array.from(c, toHex).join('');
  return `${s.slice(0,8)}-${s.slice(8,12)}-${s.slice(12,16)}-${s.slice(16,20)}-${s.slice(20)}`;
}
