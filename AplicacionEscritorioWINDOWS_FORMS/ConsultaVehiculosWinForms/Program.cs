namespace ConsultaVehiculosWinForms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        // Inicializa la configuración estándar de Windows Forms en .NET 8.
        ApplicationConfiguration.Initialize();
        Application.Run(new FormPrincipal());
    }
}
