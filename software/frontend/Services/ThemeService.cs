using MudBlazor;

namespace Services;

public class ThemeService
{
    public MudTheme RITColorTheme { get; private set; }


    public ThemeService()
    {
        RITColorTheme = new MudTheme()
        {
            Palette = new Palette()
            {
                Primary = "#F76902",
                Secondary = "#FFFFFF",
                TextPrimary = "#000000",
                Background = "#FAFAFA",
                Surface = "#FFFFFF",
                DrawerBackground = "#FFFFFF",
                DrawerText = "#F76902",
                DrawerIcon = "#000000",
                AppbarBackground = "#F76902",
            },
            PaletteDark = new Palette()
            {
                Primary = "#F76902",
                Secondary = "#000000",
                TextPrimary = "#FFFFFF",
                Background = "#181818",
                Surface = "#1F1F1F",
                DrawerBackground = "#000000",
                DrawerText = "#F76902",
                DrawerIcon = "#FFFFFF",
                AppbarBackground = "#F76902",
            },
        };
    }
}
