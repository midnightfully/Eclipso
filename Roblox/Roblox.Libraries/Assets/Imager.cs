using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Formats;

namespace Roblox.Libraries;

public enum ImagerFormat
{
    Undefined = 0,
    PNG = 1,
    JPEG,
    GIF,
    BMP,
}

public class UnsupportedImageFormatException : Exception
{
    
}

/// <summary>
/// Generic parse error, e.g. image format is not supported, image is corrupted, image is invalid
/// </summary>
public class InvalidImageException : Exception
{
    
}

public class Imager
{
    private Stream content { get; set; }

    public int height { get; private set; } = 0;
    public int width { get; private set; } = 0;
    public ImagerFormat imageFormat { get; private set; } = ImagerFormat.Undefined;
    
    private Image image { get; set; }
    private IImageFormat format { get; set; }
    
    private Imager(Stream content)
    {
        this.content = content;
    }

    private async Task InitializeAsync()
    {
        Image imageData;
        IImageFormat imageFormat;
        try
        {
            (imageData, imageFormat) = await SixLabors.ImageSharp.Image.LoadWithFormatAsync(content);
        }
        catch (Exception e) when (e is UnknownImageFormatException or InvalidImageContentException)
        {
            throw new InvalidImageException();
        }

        this.image = imageData;
        this.format = imageFormat;
        height = imageData.Height;
        width = imageData.Width;
        this.imageFormat = format.Name switch
        {
            "PNG" => ImagerFormat.PNG,
            "JPEG" => ImagerFormat.JPEG,
            "GIF" => ImagerFormat.GIF,
            "BMP" => ImagerFormat.BMP,
            _ => throw new UnsupportedImageFormatException()
        };
    }

    public static async Task<Imager> ReadAsync(Stream content)
    {
        var img = new Imager(content);
        await img.InitializeAsync();
        return img;
    }

    /// <summary>
    /// Validates an uploaded picture and returns a freshly encoded PNG copy. Only PNG/JPEG within the size limits
    /// are accepted; dimensions are read from the header before decoding, so huge images are refused cheaply.
    /// Re-encoding drops metadata and any trailing data, so the stored file is only ever a plain PNG.
    /// </summary>
    public static async Task<MemoryStream> SanitizeToPngAsync(Stream content, int maxDimension, long maxBytes)
    {
        if (content.CanSeek && content.Length > maxBytes)
            throw new ImageRejectedException($"The image is larger than {maxBytes / (1024 * 1024)} MB.");
        var buffer = new MemoryStream();
        await content.CopyToAsync(buffer);
        if (buffer.Length > maxBytes)
            throw new ImageRejectedException($"The image is larger than {maxBytes / (1024 * 1024)} MB.");
        if (buffer.Length == 0)
            throw new ImageRejectedException("The file is empty.");
        buffer.Position = 0;
        IImageInfo? info;
        IImageFormat? detected;
        try
        {
            (info, detected) = await Image.IdentifyWithFormatAsync(buffer);
        }
        catch (Exception)
        {
            info = null; detected = null;
        }
        if (info == null || detected == null)
            throw new ImageRejectedException("The file is not a readable image. Upload a PNG or JPEG.");
        if (detected.Name != "PNG" && detected.Name != "JPEG")
            throw new ImageRejectedException($"{detected.Name} images are not supported. Upload a PNG or JPEG.");
        if (info.Width < 1 || info.Height < 1 || info.Width > maxDimension || info.Height > maxDimension)
            throw new ImageRejectedException($"The image is {info.Width}x{info.Height}; the maximum is {maxDimension}x{maxDimension} pixels.");
        buffer.Position = 0;
        try
        {
            using var image = await Image.LoadAsync(buffer);
            image.Metadata.ExifProfile = null;
            image.Metadata.XmpProfile = null;
            image.Metadata.IccProfile = null;
            var output = new MemoryStream();
            await image.SaveAsPngAsync(output);
            output.Position = 0;
            return output;
        }
        catch (Exception e) when (e is UnknownImageFormatException or InvalidImageContentException or ImageFormatException)
        {
            throw new ImageRejectedException("The image is damaged and could not be read.");
        }
    }
}

/// <summary>An uploaded image was refused; the message is safe to show to the uploader.</summary>
public class ImageRejectedException : Exception
{
    public ImageRejectedException(string message) : base(message) { }
}
