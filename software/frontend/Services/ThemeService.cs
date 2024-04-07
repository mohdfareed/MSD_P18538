using MudBlazor;

namespace Services;

public class ThemeService
{
    public MudTheme RITColorTheme { get; private set; } = new MudTheme();


    public ThemeService()
    {
        RITColorTheme.Palette.Primary = "#F76902";
        RITColorTheme.Palette.Secondary = "#FFFFFF";
        RITColorTheme.Palette.TextPrimary = "#000000";
        RITColorTheme.Palette.Background = "#FAFAFA";
        RITColorTheme.Palette.Surface = "#FFFFFF";
        RITColorTheme.Palette.DrawerBackground = "#FFFFFF";
        RITColorTheme.Palette.DrawerText = "#F76902";
        RITColorTheme.Palette.DrawerIcon = "#000000";
        RITColorTheme.Palette.AppbarBackground = "#F76902";

        RITColorTheme.PaletteDark.Primary = "#F76902";
        RITColorTheme.PaletteDark.Secondary = "#000000";
        RITColorTheme.PaletteDark.TextPrimary = "#FFFFFF";
        RITColorTheme.PaletteDark.Background = "#181818";
        RITColorTheme.PaletteDark.Surface = "#1F1F1F";
        RITColorTheme.PaletteDark.DrawerBackground = "#000000";
        RITColorTheme.PaletteDark.DrawerText = "#F76902";
        RITColorTheme.PaletteDark.DrawerIcon = "#FFFFFF";
        RITColorTheme.PaletteDark.AppbarBackground = "#F76902";
    }
}
