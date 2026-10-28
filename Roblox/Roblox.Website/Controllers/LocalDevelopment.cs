using System.Net;
using System.ComponentModel.DataAnnotations;
using System.Security.Cryptography;
using Dapper;
using Microsoft.AspNetCore.Mvc;
using Npgsql;
using Roblox.Models.Users;
using Roblox.Website.Middleware;

namespace Roblox.Website.Controllers;

[ApiController]
[Route("local")]
public class LocalDevelopmentController : ControllerBase
{
    private readonly NpgsqlConnection db;
    public LocalDevelopmentController(NpgsqlConnection connection) { db = connection; }
    private void Check()
    {
        if (!Roblox.Configuration.LocalDevelopment || !Roblox.Configuration.LocalTestEndpointsEnabled || HttpContext.Connection.RemoteIpAddress == null ||
            !IPAddress.IsLoopback(HttpContext.Connection.RemoteIpAddress))
            throw new Roblox.Services.Exceptions.RobloxException(404, 0, "Not found");
        var origin = Request.Headers.Origin.ToString();
        if (origin.Length > 0 && origin != Roblox.Configuration.BaseUrl)
            throw new Roblox.Exceptions.ForbiddenException();
    }
    [HttpGet("")]
    public IActionResult Page()
    {
        Check();
        return Content(System.IO.File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"LocalDashboard.html")), "text/html");
    }
    public class Credentials
    {
        [Required] public string username { get; set; } = "";
        [Required] public string password { get; set; } = "";
    }
    [HttpPost("signup")]
    public async Task<dynamic> Signup(Credentials request)
    {
        Check();
        if (!await services.users.IsUsernameValid(request.username) || !services.users.IsPasswordValid(request.password))
            throw new Roblox.Exceptions.BadRequestException(0,"Use a valid username and a stronger password.");
        if (!await services.users.IsNameAvailableForSignup(request.username))
            throw new Roblox.Exceptions.BadRequestException(0,"Username already taken.");
        var user = await services.users.CreateUser(request.username,request.password,Gender.Male);
        await SetSession(user.userId);
        return new { user.userId };
    }
    private async Task SetSession(long userId)
    {
        var id = await services.users.CreateSession(userId);
        var cookie = SessionMiddleware.CreateJwt(new JwtEntry { sessionId=id,createdAt=DateTimeOffset.UtcNow.ToUnixTimeSeconds() });
        Response.Cookies.Append(SessionMiddleware.CookieName,cookie,new CookieOptions {HttpOnly=true,SameSite=SameSiteMode.Lax,Secure=false,Path="/",Expires=DateTimeOffset.UtcNow.AddDays(7)});
    }
    [HttpPost("login")]
    public async Task<dynamic> Login(Credentials request)
    {
        Check();
        var id=await services.users.GetUserIdFromUsername(request.username);
        if (!await services.users.VerifyPassword(id,request.password)) throw new Roblox.Exceptions.ForbiddenException(0,"Incorrect password.");
        await SetSession(id);
        return new { userId=id };
    }
    [HttpGet("state")]
    public async Task<dynamic> State()
    {
        Check();
        var catalog=await db.QueryAsync("SELECT id,name,price_robux AS price,is_for_sale AS for_sale,is_limited,is_limited_unique,serial_count,sale_count,creator_id FROM asset WHERE id BETWEEN 900001 AND 900003 ORDER BY id");
        if(userSession==null) return new { loggedIn=false,catalog };
        var id=safeUserSession.userId;
        var inventory=await db.QueryAsync("SELECT ua.id,ua.asset_id,a.name,ua.serial,ua.price,a.is_limited,a.is_limited_unique,a.is_for_sale FROM user_asset ua JOIN asset a ON a.id=ua.asset_id WHERE ua.user_id=@id ORDER BY ua.id",new{id});
        var history=await db.QueryAsync("SELECT id,type,amount,asset_id,created_at FROM user_transaction WHERE user_id_one=@id ORDER BY id DESC LIMIT 25",new{id});
        return new { loggedIn=true,userId=id,username=safeUserSession.username,balance=await services.economy.GetUserBalance(id),catalog,inventory,history };
    }
    [HttpPost("grant")]
    public async Task<dynamic> Grant()
    {
        Check();
        var id=safeUserSession.userId;
        await db.OpenAsync();
        await using var tx=await db.BeginTransactionAsync();
        var balance=await db.QuerySingleAsync<int>("UPDATE user_economy SET balance_robux=LEAST(balance_robux+10000,1000000) WHERE user_id=@id RETURNING balance_robux",new{id},tx);
        await db.ExecuteAsync("INSERT INTO local_grant_log(user_id,balance_after) VALUES (@id,@balance)",new{id,balance},tx);
        await tx.CommitAsync();
        return new { robux=balance };
    }
    [HttpPost("seed")]
    public async Task<dynamic> Seed()
    {
        Check();
        long? seller=await db.QuerySingleOrDefaultAsync<long?>("SELECT id FROM \"user\" WHERE id=1 AND username='Roblox'");
        if(seller==null) throw new InvalidOperationException("The Roblox system account must exist as user 1 before seeding.");
        await db.ExecuteAsync(@"INSERT INTO asset(id,name,description,asset_type,asset_genre,creator_type,creator_id,moderation_status,is_for_sale,price_robux,is_limited,is_limited_unique,serial_count)
VALUES(900001,'Local Test Cap','Local test fixture: ordinary catalog purchase.',8,0,1,@seller,1,true,25,false,false,null),
(900002,'Local Limited Crown','Local test fixture: three serial-numbered copies.',8,0,1,@seller,1,true,100,false,true,3),
(900003,'Local Resale Shades','Local test fixture: resale-only limited.',8,0,1,@seller,1,false,250,true,false,null)
ON CONFLICT(id) DO NOTHING",new{seller});
        await db.ExecuteAsync(@"INSERT INTO user_asset(user_id,asset_id,serial,price) SELECT @seller,900003,1,250 WHERE NOT EXISTS(SELECT 1 FROM user_asset WHERE asset_id=900003)",new{seller});
        return new { seeded=true,seller };
    }
}
