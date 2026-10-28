using System.ComponentModel.DataAnnotations;
namespace Roblox.Website.WebsiteModels;
public class SignUpRequest
{
    // Validated at registration; a full date of birth is not persisted.
    [Required] public string birthday { get; set; } = "";
    [Required] public string gender { get; set; } = "";
    [Required, StringLength(128, MinimumLength = 8)] public string password { get; set; } = "";
    [Required, StringLength(20, MinimumLength = 3)] public string username { get; set; } = "";
    public bool acceptTerms { get; set; }
}
public class SignupResponse
{
    public long userId { get; set; }
}
