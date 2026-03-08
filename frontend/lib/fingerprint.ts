import fpPromise from '@fingerprintjs/fingerprintjs';

async function getRawFingerprint(): Promise<string> {
    const fp = await fpPromise.load();
    const result = await fp.get();
    return result.visitorId;
}

// Client-side SHA-256 implementation using Web Crypto API
async function sha256(message: string): Promise<string> {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}

/**
 * Gets the browser fingerprint and hashes it client-side.
 * The raw fingerprint is never transmitted.
 */
export async function getFingerprintHash(): Promise<string> {
    try {
        const rawId = await getRawFingerprint();
        const hash = await sha256(rawId);
        return hash;
    } catch (error) {
        console.error("Failed to generate fingerprint", error);
        // Fallback if fingerprinting fails (e.g., highly restrictive browser)
        // We generate a random hash for this session so they can still participate,
        // but they lose cross-session identity.
        return sha256(Math.random().toString());
    }
}
