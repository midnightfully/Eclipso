using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using Roblox.Exceptions;
using Roblox.Models.Sessions;
using Roblox.Models.Users;
using Roblox.Services;
using Roblox.Services.App.FeatureFlags;
using Roblox.Services.Exceptions;
using Roblox.Website.WebsiteModels;
using Roblox.Website.WebsiteModels.Authentication;
using BadRequestException = Roblox.Exceptions.BadRequestException;
using ServiceProvider = Microsoft.Extensions.DependencyInjection.ServiceProvider;

namespace Roblox.Website.Controllers;

[ApiController]
[Route("/apisite/auth/v2")]
public class AuthenticationControllerV2 : ControllerBase
{
	public class Enable2FARequest
    {
        public string Code { get; set; }
    }
	
	public class Disable2FARequest
    {
        public string Code { get; set; }
    }
	
	[HttpGet("user/two-step/setup")]
	public async Task<dynamic> Get2FASetup()
	{
		var isEnabled = await services.twoFactor.IsEnabled(safeUserSession.userId);
		if (isEnabled)
		{
			return new
			{
				enabled = true,
			};
		}

		var Secret = await services.twoFactor.Setup(safeUserSession.userId);
		return new
		{
			enabled = false,
			totp = Secret
		};
	}

	
	[HttpPost("user/two-step/enable")]
	public async Task Enable2FA([FromBody] Enable2FARequest request)
	{
		var isValid = await services.twoFactor.VerifyCode(safeUserSession.userId, request.Code);
		if (!isValid)
		{
			throw new BadRequestException(0, "Bad or expired code");
		}

		await services.twoFactor.MarkEnabled(safeUserSession.userId);
	}
	
	[HttpPost("user/two-step/disable")]
	public async Task Disable2FA([FromBody] Disable2FARequest request)
	{
		var isEnabled = await services.twoFactor.IsEnabled(safeUserSession.userId);
		if (!isEnabled)
		{
			throw new BadRequestException(0, "2FA is not enabled");
		}

		var isValid = await services.twoFactor.VerifyCode(safeUserSession.userId, request.Code);
		if (!isValid)
		{
			throw new BadRequestException(1, "Bad 2FA code");
		}

		await services.twoFactor.Disable2FA(safeUserSession.userId);
	}

    [HttpGet("metadata")]
    public dynamic GetMetadata()
    {
        return new
        {
            cookieLawNoticeTimeout = 20 * 1000,
        };
    }

    [HttpGet("passwords/current-status")]
    public dynamic GetPasswordStatus()
    {
        return new
        {
            valid = true,
        };
    }

    [HttpPost("user/passwords/change")]
    public async Task ChangePassword([Required, FromBody] ChangePasswordRequest request)
    {
        FeatureFlags.FeatureCheck(FeatureFlag.ChangePasswordEnabled);
        var passwordOk = services.users.IsPasswordValid(request.newPassword);
        if (!passwordOk)
        {
            throw new BadRequestException(0, "Invalid password");
        }
        // Pass cooldown check
/*         if (!await services.cooldown.TryCooldownCheck("change password " + safeUserSession.userId,
                TimeSpan.FromMinutes(1)))
            throw new RobloxException(429, 0, "TooManyRequests"); */
        // Verify password
        var correctPass = await services.users.VerifyPassword(safeUserSession.userId, request.currentPassword);
        if (!correctPass)
        {
            throw new BadRequestException(8, "Password does not match");
        }
        // We can update the user's password now
        await services.users.ChangePassword(safeUserSession.userId, request.newPassword);
    }

    [HttpPost("logout")]
    public async Task Logout()
    {
        await services.users.DeleteSession(safeUserSession.sessionId);
        using var sessCache = Roblox.Services.ServiceProvider.GetOrCreate<UserSessionsCache>();
        sessCache.Remove(safeUserSession.sessionId);
        HttpContext.Response.Cookies.Delete(Middleware.SessionMiddleware.CookieName);
    }

    private async Task CreateSessionAndSetCookie(long userId)
    {
        var sess = await services.users.CreateSession(userId);
        var sessionCookie = Roblox.Website.Middleware.SessionMiddleware.CreateJwt(new Middleware.JwtEntry()
        {
            sessionId = sess,
            createdAt = DateTimeOffset.Now.ToUnixTimeSeconds(),
        });
        HttpContext.Response.Cookies.Append(Middleware.SessionMiddleware.CookieName, sessionCookie, new CookieOptions()
        {
            Secure = !Roblox.Configuration.LocalDevelopment,
            Expires = DateTimeOffset.Now.Add(TimeSpan.FromDays(364)),
            IsEssential = true,
            HttpOnly = true,
            Path = "/",
            SameSite = SameSiteMode.Lax,
        });
    }

    [HttpPost("login")]
    public async Task Login([Required, FromBody] LoginRequest request)
    {
        FeatureFlags.FeatureCheck(FeatureFlag.LoginEnabled);
        if (request.ctype != "username")
        {
            throw new BadRequestException(0, "Login type is not supported.");
        }

        long userId;
        try
        {
            userId = await services.users.GetUserIdFromUsername(request.cvalue);
        }
        catch (RecordNotFoundException e)
        {
            throw new ForbiddenException(1, "Incorrect username or password. Please try again");
        }

        var passwordOk = await services.users.VerifyPassword(userId, request.password);
        if (!passwordOk)
        {
            throw new ForbiddenException(1, "Incorrect username or password. Please try again");
        }

        await CreateSessionAndSetCookie(userId);
    }

    [HttpPost("signup")]
    public async Task<SignupResponse> Signup([Required, FromBody] SignUpRequest request)
    {
        FeatureFlags.FeatureCheck(FeatureFlag.SignupEnabled);
        if (!request.acceptTerms)
            throw new BadRequestException(10, "Accept the revival terms before creating an account.");
        if (!DateOnly.TryParseExact(request.birthday, "yyyy-MM-dd", System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.None, out var birthday) ||
            birthday > DateOnly.FromDateTime(DateTime.UtcNow) || birthday.Year < 1900)
            throw new BadRequestException(11, "Choose a valid birthday.");
        if (!Enum.TryParse<Gender>(request.gender, true, out var gender) || !Enum.IsDefined(gender))
            throw new BadRequestException(12, "Choose a valid gender option.");
        if (!await services.users.IsUsernameValid(request.username))
            throw new BadRequestException(5, "Choose a valid username using 3–20 characters.");
        if (!services.users.IsPasswordValid(request.password))
            throw new BadRequestException(9, "Choose a stronger password with at least eight characters.");
        await services.cooldown.CooldownCheck("signup:ip:" + GetIP(), TimeSpan.FromSeconds(5));
        if (!await services.users.IsNameAvailableForSignup(request.username))
            throw new BadRequestException(6, "Username is already taken.");
        try
        {
            var created = await services.users.CreateUser(request.username, request.password, gender);
            await CreateSessionAndSetCookie(created.userId);
            return new SignupResponse { userId = created.userId };
        }
        catch (UsersService.UsernameTakenException)
        {
            throw new BadRequestException(6, "Username is already taken.");
        }
    }

    [HttpPost("logoutfromallsessionsandreauthenticate")]
    public async Task LogoutFromAllSessionsAndReAuthenticate()
    {
        // We don't actually re authenticate (for security).
        await services.users.ExpireAllSessions(safeUserSession.userId);
        // remove current session immediately
        using var sessCache = Roblox.Services.ServiceProvider.GetOrCreate<UserSessionsCache>();
        sessCache.Remove(safeUserSession.sessionId);
    }
}