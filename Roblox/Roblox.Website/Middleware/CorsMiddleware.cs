using Microsoft.AspNetCore.Http.Extensions;

namespace Roblox.Website.Middleware;

public class RobloxPlayerCorsMiddleware
{
    private RequestDelegate _next;
    public RobloxPlayerCorsMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    private static string CdnSource()
    {
        // Allow the configured CDN/asset origin, if any (scheme + host only).
        if (Uri.TryCreate(Roblox.Configuration.CdnBaseUrl, UriKind.Absolute, out var cdn))
            return " " + cdn.GetLeftPart(UriPartial.Authority);
        return "";
    }

    private string GenerateCspHeader(bool isAuthenticated)
    {
        // Only this site's own origin and the explicitly configured CDN are trusted. The upstream policy
        // trusted the original developer's domains (bbblox.org, zawg.ca), which blocked every local image
        // and let foreign origins be framed or contacted; those entries were removed.
        var cdn = CdnSource();
        var connectSrc = "'self' https://hcaptcha.com https://*.hcaptcha.com" + cdn;
#if DEBUG
        connectSrc += " ws://localhost:* ws://127.0.0.1:*"; // Next.js dev hot reload
#endif
        var imgSrc = "'self' data: blob:" + cdn;
        // unsafe-eval required by nextjs
        var scriptSrc =
            "'unsafe-eval' 'self' https://hcaptcha.com https://*.hcaptcha.com https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" + cdn;

        return "default-src 'self'; img-src " + imgSrc + "; child-src 'self'; script-src " + scriptSrc + "; frame-src 'self' https://hcaptcha.com https://*.hcaptcha.com; style-src 'unsafe-inline' 'self' https://fonts.googleapis.com https://hcaptcha.com https://*.hcaptcha.com https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" + cdn + "; font-src 'self' https://fonts.gstatic.com" + cdn + "; connect-src " + connectSrc + "; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; frame-ancestors 'self';";
    }
    
    public async Task InvokeAsync(HttpContext ctx)
    {
        var isAuthenticated = ctx.Items.ContainsKey(".ROBLOSECURITY");
        ctx.Response.Headers["Cross-Origin-Opener-Policy"] = "same-origin";
        ctx.Response.Headers["Cross-Origin-Resource-Policy"] = "cross-origin";
        ctx.Response.Headers["X-Frame-Options"] = "SAMEORIGIN";
        ctx.Response.Headers["X-XSS-Protection"] = "1; mode=block";
        ctx.Response.Headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains";
        ctx.Response.Headers["X-Content-Type-Options"] = "nosniff";
        ctx.Response.Headers["Content-Security-Policy"] = GenerateCspHeader(isAuthenticated);
        await _next(ctx);
    }
}

public static class RobloxPlayerCorsMiddlewareExtensions
{
    public static IApplicationBuilder UseRobloxPlayerCorsMiddleware(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<RobloxPlayerCorsMiddleware>();
    }
}
