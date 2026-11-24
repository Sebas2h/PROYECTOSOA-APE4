using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;

namespace ConsultaVehiculosWinForms;

public partial class FormPrincipal : Form
{
    // El endpoint real está definido en VehiculoController.java.
    private static readonly string UrlJava =
        (Environment.GetEnvironmentVariable("APE04_BASE_URL")
         ?? "http://127.0.0.1:8090").TrimEnd('/') + "/";

    // Se reutiliza un solo cliente HTTP durante toda la aplicación.
    internal static readonly HttpClient ClienteHttp = new()
    {
        BaseAddress = new Uri(UrlJava),
        Timeout = TimeSpan.FromSeconds(15)
    };

    public FormPrincipal()
    {
        InitializeComponent();
    }

    internal string ObtenerToken()
    {
        string token = txtToken.Text.Trim();
        return token.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase)
            ? token[7..].Trim()
            : token;
    }

    // Este es el único botón de la ventana: llama a Spring Boot y llena la grilla.
    private async void btnConsultar_Click(object? sender, EventArgs e)
    {
        string token = ObtenerToken();

        if (string.IsNullOrWhiteSpace(token))
        {
            MostrarEstado("Pegue primero el token JWT obtenido en Postman.", esError: true);
            txtToken.Focus();
            return;
        }

        btnConsultar.Enabled = false;
        MostrarEstado("Consultando API Java...");

        try
        {
            // GET /api/vehiculos. El token se envía como Authorization: Bearer.
            using var solicitud = new HttpRequestMessage(HttpMethod.Get, "api/vehiculos");
            solicitud.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

            using HttpResponseMessage respuesta = await ClienteHttp.SendAsync(solicitud);

            if (respuesta.StatusCode == HttpStatusCode.Unauthorized)
            {
                LimpiarDatos();
                MostrarEstado("HTTP 401: JWT inválido o vencido. Genere un token nuevo.", esError: true);
                return;
            }

            if (respuesta.StatusCode == HttpStatusCode.Forbidden)
            {
                LimpiarDatos();
                MostrarEstado("HTTP 403: el usuario no tiene permiso de consulta.", esError: true);
                return;
            }

            if (!respuesta.IsSuccessStatusCode)
            {
                LimpiarDatos();
                MostrarEstado($"Error HTTP {(int)respuesta.StatusCode} al consultar Java.", esError: true);
                return;
            }

            // VehiculoController devuelve un arreglo JSON, no un objeto con 'data'.
            string contenidoJson = await respuesta.Content.ReadAsStringAsync();
            List<Vehiculo> lista = JsonSerializer.Deserialize<List<Vehiculo>>(
                contenidoJson,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
                ?? new List<Vehiculo>();

            dgvVehiculos.DataSource = null;
            dgvVehiculos.DataSource = lista;
            lblTotal.Text = $"Total de vehículos: {lista.Count}";
            MostrarEstado(lista.Count == 0
                ? "HTTP 200: la API respondió, pero no hay vehículos registrados."
                : "HTTP 200: consulta realizada correctamente.");
        }
        catch (HttpRequestException)
        {
            LimpiarDatos();
            MostrarEstado("No se pudo conectar. Compruebe Spring Boot en localhost:8080.", esError: true);
        }
        catch (TaskCanceledException)
        {
            LimpiarDatos();
            MostrarEstado("La API no respondió dentro de los 15 segundos.", esError: true);
        }
        catch (JsonException)
        {
            LimpiarDatos();
            MostrarEstado("La respuesta no tiene el JSON esperado de vehículos.", esError: true);
        }
        finally
        {
            btnConsultar.Enabled = true;
        }
    }

    private void btnCrearVehiculo_Click(object? sender, EventArgs e)
    {
        if (!ValidarToken()) return;
        using var formulario = new FormCrearVehiculo(ObtenerToken());
        formulario.ShowDialog(this);
        if (formulario.VehiculoCreado) btnConsultar.PerformClick();
    }

    private void btnCrearComprador_Click(object? sender, EventArgs e)
    {
        if (!ValidarToken()) return;
        using var formulario = new FormCrearComprador(ObtenerToken());
        formulario.ShowDialog(this);
    }

    private void btnListarCompradores_Click(object? sender, EventArgs e)
    {
        if (!ValidarToken()) return;
        using var formulario = new FormCompradores(ObtenerToken());
        formulario.ShowDialog(this);
    }

    private void btnListarVentas_Click(object? sender, EventArgs e)
    {
        if (!ValidarToken()) return;
        using var formulario = new FormVentas(ObtenerToken());
        formulario.ShowDialog(this);
    }

    private bool ValidarToken()
    {
        if (!string.IsNullOrWhiteSpace(ObtenerToken())) return true;
        LimpiarDatos();
        MostrarEstado("Ingrese primero el JWT que se usará en todas las operaciones.", esError: true);
        txtToken.Focus();
        return false;
    }

    private void txtToken_TextChanged(object? sender, EventArgs e)
    {
        if (!string.IsNullOrWhiteSpace(ObtenerToken())) return;
        LimpiarDatos();
        MostrarEstado("Ingrese un JWT para consultar o administrar datos.");
    }

    private void LimpiarDatos()
    {
        dgvVehiculos.DataSource = null;
        lblTotal.Text = "Total de vehículos: 0";
    }

    private void MostrarEstado(string mensaje, bool esError = false)
    {
        lblEstado.ForeColor = esError ? Color.Firebrick : Color.FromArgb(50, 64, 76);
        lblEstado.Text = mensaje;
    }

    private void lblTitulo_Click(object? sender, EventArgs e)
    {

    }
}
