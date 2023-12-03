using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using Microsoft.AspNetCore.Cors;
using Frontend;
using MudBlazor.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// services
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
builder.Services.AddScoped<Services.TranscriptionService>();
builder.Services.AddMudServices();

// global settings
var settings = new Models.GlobalSettings();
builder.Configuration.Bind(settings);
builder.Services.AddSingleton(settings);

// cors
builder.Services.AddCors(options =>
{
    options.AddPolicy("CorsPolicy", builder =>
    {
        builder.WithOrigins(settings.BackendBaseAddress)
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

var app = builder.Build();
await app.RunAsync();
