using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using Frontend;
using MudBlazor.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// services
var uri = new Uri(builder.HostEnvironment.BaseAddress);
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = uri });
builder.Services.AddScoped<Services.ConfigurationService>();
builder.Services.AddScoped<Services.TranscriptionService>();
builder.Services.AddScoped<Services.AudioService>();
builder.Services.AddMudServices();

// global settings
var settings = new Models.GlobalSettings();
builder.Configuration.Bind(settings);
builder.Services.AddSingleton(settings);

var app = builder.Build();
await app.RunAsync();
