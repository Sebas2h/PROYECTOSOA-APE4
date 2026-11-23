using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;

namespace ConsultaVehiculosWinForms;

public partial class FormPrincipal : Form
{
    // El endpoint real está definido en VehiculoController.java.
    private const string UrlJava = "http://127.0.0.1:8080/";

    // Se reutiliza un solo cliente HTTP durante toda la aplicación.
    private static readonly HttpClient ClienteHttp = new()
    {
        BaseAddress = new Uri(UrlJava),
        Timeout = TimeSpan.FromSeconds(15)
    };

    public FormPrincipal()
    {
        InitializeComponent();
    }

    // Este es el único botón de la ventana: llama a Spring Boot y llena la grilla.
    private async void btnConsultar_Click(object? sender, EventArgs e)
    {
        string token = txtToken.Text.Trim();


        if (token.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
        {
            token = token[7..].Trim();
        }

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

    private void lblTitulo_Click(object sender, EventArgs e)
    {

    }
}
