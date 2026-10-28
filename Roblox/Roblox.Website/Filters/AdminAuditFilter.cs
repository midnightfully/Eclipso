using System.Text.Json;
using Dapper;
using Microsoft.AspNetCore.Mvc.Controllers;
using Microsoft.AspNetCore.Mvc.Filters;
using Roblox.Models.Sessions;

namespace Roblox.Website.Filters;

/// <summary>
/// Records every state-changing admin API request, and every denied admin request, in admin_audit_log.
/// Applied to the whole admin controller so coverage does not depend on individual actions remembering to log.
/// Runs outside the per-action StaffFilter, so requests rejected by it are recorded too.
/// </summary>
public class AdminAuditFilter : ActionFilterAttribute, IAsyncActionFilter
{
    private static readonly string[] SecretKeyFragments = { "password", "token", "secret", "cookie", "authorization", "key" };
    private const int MaxParameterLength = 4000;

    public override async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
    {
        var http = context.HttpContext;
        var isMutation = !HttpMethods.IsGet(http.Request.Method) && !HttpMethods.IsHead(http.Request.Method);
        var parameters = SerializeParameters(context.ActionArguments);
        Exception? failure = null;
        ActionExecutedContext? executed = null;
        try
        {
            executed = await next();
            failure = executed.Exception is { } e && !executed.ExceptionHandled ? e : null;
        }
        catch (Exception e)
        {
            failure = e;
            throw;
        }
        finally
        {
            // Action filters run before the result executes, so take the status from the result itself.
            var status = failure is Roblox.Exceptions.IHttpException httpEx
                ? (int)httpEx.statusCode
                : failure != null ? 500
                : executed?.Result is Microsoft.AspNetCore.Mvc.Infrastructure.IStatusCodeActionResult { StatusCode: { } code } ? code
                : executed?.Result is Microsoft.AspNetCore.Mvc.RedirectResult ? 302
                : http.Response.StatusCode;
            // GETs are only recorded when they were refused, so probing by non-staff is visible.
            if (isMutation || status is 401 or 403)
                await Record(context, (http.Items[".ROBLOSECURITY"] as UserSession)?.userId, status, parameters, failure);
        }
    }

    private static async Task Record(ActionExecutingContext context, long? actorId, int status, string? parameters, Exception? failure)
    {
        try
        {
            var action = (context.ActionDescriptor as ControllerActionDescriptor)?.ActionName ?? "unknown";
            var outcome = status < 400 ? "success" : status is 401 or 403 ? "denied" : "failed";
            // HTTP exceptions keep their user-facing reason in errors; the Exception.Message is generic.
            var reason = failure is Roblox.Exceptions.IHttpException h
                ? h.errors.Select(x => x.errorMessage).FirstOrDefault(m => !string.IsNullOrEmpty(m))
                : failure?.Message;
            if (!string.IsNullOrEmpty(reason))
                outcome += ": " + Truncate(reason, 300);
            await using var db = Roblox.Services.Database.connection;
            await db.ExecuteAsync(
                "INSERT INTO admin_audit_log (actor_user_id, method, path, action, parameters, status_code, outcome) " +
                "VALUES (:actor, :method, :path, :action, CAST(:parameters AS jsonb), :status, :outcome)",
                new
                {
                    actor = actorId,
                    method = context.HttpContext.Request.Method,
                    path = Truncate(context.HttpContext.Request.Path.Value ?? "", 500),
                    action,
                    parameters,
                    status,
                    outcome,
                });
        }
        catch (Exception e)
        {
            // Never fail an admin request because auditing failed, but make the gap visible in the logs.
            Console.WriteLine("[AdminAudit] failed to record audit entry: {0}", e.Message);
        }
    }

    private static string? SerializeParameters(IDictionary<string, object?> arguments)
    {
        if (arguments.Count == 0) return null;
        var safe = new Dictionary<string, object?>();
        foreach (var (name, value) in arguments)
            safe[name] = Sanitize(name, value, 0);
        var json = JsonSerializer.Serialize(safe);
        return json.Length <= MaxParameterLength
            ? json
            : JsonSerializer.Serialize(new { truncated = Truncate(json, MaxParameterLength) });
    }

    private static object? Sanitize(string name, object? value, int depth)
    {
        if (SecretKeyFragments.Any(s => name.Contains(s, StringComparison.OrdinalIgnoreCase)))
            return "[redacted]";
        switch (value)
        {
            case null:
                return null;
            case IFormFile file:
                return new { file = file.FileName, file.Length, file.ContentType };
            case string or bool or Enum or DateTime or DateTimeOffset or Guid:
                return value is Enum ? value.ToString() : value;
            case var _ when value.GetType().IsPrimitive || value is decimal:
                return value;
            case Stream:
                return "[stream]";
        }
        if (depth >= 2) return value.ToString();
        if (value is System.Collections.IEnumerable list)
            return list.Cast<object?>().Take(50).Select(v => Sanitize(name, v, depth + 1)).ToList();
        var props = new Dictionary<string, object?>();
        foreach (var p in value.GetType().GetProperties().Where(p => p.CanRead && p.GetIndexParameters().Length == 0))
        {
            object? v;
            try { v = p.GetValue(value); } catch { continue; }
            props[p.Name] = Sanitize(p.Name, v, depth + 1);
        }
        return props;
    }

    private static string Truncate(string s, int max) => s.Length <= max ? s : s[..max];
}
