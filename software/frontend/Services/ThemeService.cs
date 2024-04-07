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
                Black = "#27272f",
                Primary = "#F76902",
                Background = "#FAFAFA",
                BackgroundGrey = "#F5F5F5",
                Surface = "#FFFFFF",
                DrawerBackground = "#FFFFFF",
                DrawerText = "#27272f",
                DrawerIcon = "#27272f",
                AppbarBackground = "#27272f",
                AppbarText = "#FFFFFF",
                TextPrimary = "#27272f",
                TextSecondary = "#757575",
                ActionDefault = "#27272f",
                ActionDisabled = "#E0E0E0",
                ActionDisabledBackground = "#F5F5F5",
                // Add other color overrides here
            },
            PaletteDark = new Palette()
            {
                Black = "#27272f",
                Primary = "#F76902",
                Background = "#FAFAFA",
                BackgroundGrey = "#F5F5F5",
                Surface = "#FFFFFF",
                DrawerBackground = "#FFFFFF",
                DrawerText = "#27272f",
                DrawerIcon = "#27272f",
                AppbarBackground = "#27272f",
                AppbarText = "#FFFFFF",
                TextPrimary = "#27272f",
                TextSecondary = "#757575",
                ActionDefault = "#27272f",
                ActionDisabled = "#E0E0E0",
                ActionDisabledBackground = "#F5F5F5",
            },
            // Can also customize Typography, ZIndex, LayoutProperties, etc.
        };
    }
}
