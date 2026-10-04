// Sicherheits-Header für Antworten aus Functions (statische Seiten bekommen sie über static/_headers)
export const SEC = {
 "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
 "X-Content-Type-Options": "nosniff",
 "X-Frame-Options": "SAMEORIGIN",
 "Referrer-Policy": "strict-origin-when-cross-origin",
 "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()",
 "Cross-Origin-Opener-Policy": "same-origin",
 "Content-Security-Policy": "default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; connect-src 'self' https://cloudflareinsights.com; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self' data:; frame-src https://www.youtube-nocookie.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'; object-src 'none'; upgrade-insecure-requests"
};
