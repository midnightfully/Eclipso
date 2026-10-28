// ReSharper disable InconsistentNaming
#pragma warning disable CS8618
namespace Roblox;

public class GameServerConfigEntry
{
    public string ip { get; set; }
    public string domain { get; set; }
    public int maxServerCount { get; set; }
}

public static class Configuration
{
    public static bool LocalDevelopment { get; set; }
    /// <summary>
    /// Security gate (default off). When false, nothing a user uploads is handed to native tools (mesh/RBXM
    /// converters, ffmpeg/ffprobe) or to RCC (thumbnail renders, game servers). Those run old native parsers and
    /// Lua on attacker-controlled files, the most likely route to the upstream's reported remote code execution.
    /// Turn on only for an isolated render/game worker, never on the public web server.
    /// </summary>
    public static bool AllowUntrustedContentProcessing { get; set; }
    /// <summary>/local/* helpers (test Robux, instant accounts, fixtures). Separate from LocalDevelopment because
    /// behind a reverse proxy every request looks like loopback. Must be false on any public server.</summary>
    public static bool LocalTestEndpointsEnabled { get; set; }
    // Explicit settings that used to be implied by LocalDevelopment (see docs/CONFIGURATION.md).
    /// <summary>New accounts need staff approval of an application before they can use the site.</summary>
    public static bool RequireSignupApproval { get; set; }
    /// <summary>Grant the upstream daily Robux/Tickets stipend on activity.</summary>
    public static bool DailyStipendEnabled { get; set; }
    /// <summary>Use the external IPHub service when hashing/checking visitor IPs.</summary>
    public static bool ExternalIpLookupEnabled { get; set; }
    /// <summary>Mark session cookies Secure (HTTPS only). Must be true on any HTTPS host.</summary>
    public static bool SecureCookies { get; set; }
    /// <summary>Header our reverse proxy overwrites with the visitor IP (Caddy: header_up). Empty = not behind a proxy.</summary>
    public static string? TrustedProxyClientIpHeader { get; set; }
    public const string UntrustedContentDisabledMessage =
        "This kind of upload is not available yet. It needs the isolated render service, which is not set up.";
    public static string CdnBaseUrl { get; set; }
    public static string StorageDirectory { get; set; }
    public static string AssetDirectory { get; set; }
    public static string PublicDirectory { get; set; }
    public static string ThumbnailsDirectory { get; set; }
    public static string GroupIconsDirectory { get; set; }
    public static string XmlTemplatesDirectory { get; set; }
    public static string JsonDataDirectory { get; set; }
    public static string AdminBundleDirectory { get; set; }
    public static string EconomyChatBundleDirectory { get; set; }
    public static string BaseUrl { get; set; }
    public static string AssetUrl { get; set; }   
	public static string GSIPAddress { get; set; }
	public static string Webhook { get; set; }
	public static string SignupWebhook { get; set; }
	public static string DiscordClientID { get; set; }
	public static string DiscordClientSecret { get; set; }
	public static string DiscordRedirect { get; set; }
	public static string DiscordForgotPasswordRedirect { get; set; }
	public static string DiscordLoginRedirect { get; set; }	
	public static string DiscordKey { get; set; }
	public static string IPSalt { get; set; }
	public static string IPHubApiKey { get; set; }
	public static string BubbamonsApiKey { get; set; }
    public static string HCaptchaPublicKey { get; set; }
    public static string HCaptchaPrivateKey { get; set; }
    public static IEnumerable<GameServerConfigEntry> GameServerIpAddresses { get; set; }
	public static IEnumerable<int> AllowedNetworkPorts { get; set; } = Array.Empty<int>();
    public static string GameServerAuthorization { get; set; }
    public static string RobloxAppPrefix { get; set; } = "bbclient://";
    public static string AssetValidationServiceUrl { get; set; }
    public static string AssetValidationServiceAuthorization { get; set; }
    public static string BotAuthorization { get; set; }
	public static string RenderAuthorization { get; set; }
    public static string RccAuthorization { get; set; }
	public static string RccServicePath { get; set; }
	public static string RccService2015Path { get; set; }
	public static string RccService2017Path { get; set; }
	public static string RccService2018Path { get; set; }
	public static string RccService2020Path { get; set; }
	public static string LuaScriptPath { get; set; }
	public static IEnumerable<string> AllowedQuietGetJson { get; set; } = Array.Empty<string>();
    // Signing secrets come from private configuration (Secrets:*). The upstream values were published in the
    // source code, so anyone could forge the cookies they sign. Fallback: a random per-process secret.
    public static string UserAgentBypassSecret { get; set; } = RandomSecret();
    public static string VerificationSecret { get; set; } = RandomSecret();
    public static string RandomSecret() => Convert.ToBase64String(System.Security.Cryptography.RandomNumberGenerator.GetBytes(48));
    public static long PackageShirtAssetId { get; set; }
    public static long PackagePantsAssetId { get; set; }
    public static long PackageLeftArmAssetId { get; set; }
    public static long PackageRightArmAssetId { get; set; }
    public static long PackageLeftLegAssetId { get; set; }
    public static long PackageRightLegAssetId { get; set; }
    public static long PackageTorsoAssetId { get; set; }
    private static IEnumerable<long>? _SignupAssetIdsMan { get; set; }
    private static IEnumerable<long>? _SignupAssetIdsFemale { get; set; }
    private static IEnumerable<long>? _SignupAvatarAssetIdsMan { get; set; }
    private static IEnumerable<long>? _SignupAvatarAssetIdsFemale { get; set; }

    public static IEnumerable<long> SignupAssetIdsMan
    {
        get => _SignupAssetIdsMan ?? ArraySegment<long>.Empty;
        set
        {
            if (_SignupAssetIdsMan != null)
                throw new Exception("Cannot set startup asset ids - they are not null.");
            _SignupAssetIdsMan = value;
        }
    }

    public static IEnumerable<long> SignupAssetIdsFemale
    {
        get => _SignupAssetIdsFemale ?? ArraySegment<long>.Empty;
        set
        {
            if (_SignupAssetIdsFemale != null)
                throw new Exception("Cannot set startup asset ids - they are not null.");
            _SignupAssetIdsFemale = value;
        }
    }

    public static IEnumerable<long> SignupAvatarAssetIdsMan
    {
        get => _SignupAvatarAssetIdsMan ?? ArraySegment<long>.Empty;
        set
        {
            if (_SignupAvatarAssetIdsMan != null)
                throw new Exception("Cannot set signup avatar asset ids, they are not null");
            _SignupAvatarAssetIdsMan = value;
        }
    }

    public static IEnumerable<long> SignupAvatarAssetIdsFemale
    {
        get => _SignupAvatarAssetIdsFemale ?? ArraySegment<long>.Empty;
        set
        {
            if (_SignupAvatarAssetIdsFemale != null)
                throw new Exception("Cannot set signup avatar asset ids, they are not null");
            _SignupAvatarAssetIdsFemale = value;
        }
    }

    public static string GameServerDomain => "bt.zawg.ca"; // set to your game server's domain
}