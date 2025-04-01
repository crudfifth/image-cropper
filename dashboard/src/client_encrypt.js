// 文字列を暗号化する
async function encryptString(text, password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );
  const derivedKey = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
      iterations: 1000,
      hash: 'SHA-256'
    },
    key,
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt']
  );
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    derivedKey,
    data
  );
  const encryptedData = new Uint8Array(iv.byteLength + ciphertext.byteLength);
  encryptedData.set(iv, 0);
  encryptedData.set(new Uint8Array(ciphertext), iv.byteLength);
  return btoa(String.fromCharCode.apply(null, encryptedData));
}

// 暗号化された文字列を復号化する
async function decryptString(ciphertext, password) {
  const decoder = new TextDecoder();
  const data = atob(ciphertext);
  const encryptedData = new Uint8Array(data.length);
  for (let i = 0; i < data.length; i++) {
    encryptedData[i] = data.charCodeAt(i);
  }
  const iv = new Uint8Array(encryptedData.slice(0, 12));
  const encryptedText = new Uint8Array(encryptedData.slice(12));
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );
  const derivedKey = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
      iterations: 1000,
      hash: 'SHA-256'
    },
    key,
    { name: 'AES-GCM', length: 256 },
    true,
    ['decrypt']
  );
  const plaintext = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: iv },
    derivedKey,
    encryptedText
  );
  return decoder.decode(plaintext);
}


export { encryptString, decryptString };