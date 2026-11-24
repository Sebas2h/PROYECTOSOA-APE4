using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace ConsultaVehiculosWinForms;

internal static class FabricaControles
{
    internal static TextBox Campo(TableLayoutPanel panel, string etiqueta, int fila, bool multilinea = false)
    {
        panel.Controls.Add(new Label { Text = etiqueta, AutoSize = true, Anchor = AnchorStyles.Left }, 0, fila);
        var campo = new TextBox { Dock = DockStyle.Fill, Multiline = multilinea };
        panel.Controls.Add(campo, 1, fila);
        return campo;
    }

    internal static HttpRequestMessage Solicitud(HttpMethod metodo, string ruta, string token, object? cuerpo = null)
    {
        var solicitud = new HttpRequestMessage(metodo, ruta);
        solicitud.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        if (cuerpo is not null) solicitud.Content = JsonContent.Create(cuerpo);
        return solicitud;
    }

    internal static async Task<string> Detalle(HttpResponseMessage respuesta)
    {
        string cuerpo = await respuesta.Content.ReadAsStringAsync();
        if (string.IsNullOrWhiteSpace(cuerpo)) return respuesta.ReasonPhrase ?? "Sin detalle";
        try
        {
            using JsonDocument json = JsonDocument.Parse(cuerpo);
            foreach (string propiedad in new[] { "detail", "message", "detalle", "title" })
                if (json.RootElement.TryGetProperty(propiedad, out var valor)) return valor.ToString();
        }
        catch (JsonException) { }
        return cuerpo.Length > 240 ? cuerpo[..240] : cuerpo;
    }
}

public sealed class FormCrearVehiculo : Form
{
    private readonly string token;
    private readonly TextBox marca, modelo, placa, chasis, anio, color, precio;
    private readonly Label estado = new() { AutoSize = true, ForeColor = Color.FromArgb(50, 64, 76) };
    private readonly Button guardar = new() { Text = "Crear vehículo", AutoSize = true };
    public bool VehiculoCreado { get; private set; }

    public FormCrearVehiculo(string token)
    {
        this.token = token;
        Text = "P02 - Crear vehículo"; Width = 620; Height = 500; StartPosition = FormStartPosition.CenterParent;
        var panel = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(22), ColumnCount = 2, RowCount = 9 };
        panel.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 130)); panel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        marca = FabricaControles.Campo(panel, "Marca", 0); modelo = FabricaControles.Campo(panel, "Modelo", 1);
        placa = FabricaControles.Campo(panel, "Placa", 2); chasis = FabricaControles.Campo(panel, "Chasis (17)", 3);
        anio = FabricaControles.Campo(panel, "Año", 4); color = FabricaControles.Campo(panel, "Color", 5);
        precio = FabricaControles.Campo(panel, "Precio", 6);
        guardar.Click += Guardar_Click; panel.Controls.Add(guardar, 1, 7); panel.Controls.Add(estado, 1, 8); Controls.Add(panel);
        AcceptButton = guardar;
    }

    private async void Guardar_Click(object? sender, EventArgs e)
    {
        if (!int.TryParse(anio.Text, out int valorAnio) || !decimal.TryParse(precio.Text, out decimal valorPrecio) ||
            string.IsNullOrWhiteSpace(marca.Text) || string.IsNullOrWhiteSpace(modelo.Text) ||
            string.IsNullOrWhiteSpace(placa.Text) || chasis.Text.Trim().Length != 17 || valorPrecio <= 0)
        { Mostrar("Revise los campos: el chasis debe tener 17 caracteres y año/precio deben ser válidos.", true); return; }
        guardar.Enabled = false; Mostrar("Enviando POST /api/vehiculos...");
        try
        {
            var cuerpo = new { marca = marca.Text.Trim(), modelo = modelo.Text.Trim(), placa = placa.Text.Trim(), chasis = chasis.Text.Trim(), anio = valorAnio, color = color.Text.Trim(), precio = valorPrecio };
            using var solicitud = FabricaControles.Solicitud(HttpMethod.Post, "api/vehiculos", token, cuerpo);
            using var respuesta = await FormPrincipal.ClienteHttp.SendAsync(solicitud);
            if (!respuesta.IsSuccessStatusCode) { Mostrar($"HTTP {(int)respuesta.StatusCode}: {await FabricaControles.Detalle(respuesta)}", true); return; }
            VehiculoCreado = true; Mostrar($"HTTP {(int)respuesta.StatusCode}: vehículo creado correctamente.");
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException) { Mostrar("No se pudo conectar con la API mediante NGINX.", true); }
        finally { guardar.Enabled = true; }
    }
    private void Mostrar(string texto, bool error = false) { estado.ForeColor = error ? Color.Firebrick : Color.DarkGreen; estado.Text = texto; }
}

public sealed class FormCrearComprador : Form
{
    private readonly string token;
    private readonly TextBox documento, nombre, correo;
    private readonly Label estado = new() { AutoSize = true };
    private readonly Button guardar = new() { Text = "Crear comprador", AutoSize = true };
    public FormCrearComprador(string token)
    {
        this.token = token; Text = "P04 - Crear comprador"; Width = 600; Height = 330; StartPosition = FormStartPosition.CenterParent;
        var panel = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(22), ColumnCount = 2, RowCount = 5 };
        panel.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 130)); panel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        documento = FabricaControles.Campo(panel, "Documento", 0); nombre = FabricaControles.Campo(panel, "Nombre", 1); correo = FabricaControles.Campo(panel, "Correo", 2);
        guardar.Click += Guardar_Click; panel.Controls.Add(guardar, 1, 3); panel.Controls.Add(estado, 1, 4); Controls.Add(panel); AcceptButton = guardar;
    }
    private async void Guardar_Click(object? sender, EventArgs e)
    {
        if (documento.Text.Trim().Length < 3 || nombre.Text.Trim().Length < 2 || !correo.Text.Contains('@')) { Mostrar("Complete documento, nombre y un correo válido.", true); return; }
        guardar.Enabled = false; Mostrar("Enviando POST /api/compradores...");
        try
        {
            var cuerpo = new { documento = documento.Text.Trim(), nombre = nombre.Text.Trim(), correo = correo.Text.Trim() };
            using var solicitud = FabricaControles.Solicitud(HttpMethod.Post, "api/compradores", token, cuerpo);
            using var respuesta = await FormPrincipal.ClienteHttp.SendAsync(solicitud);
            if (!respuesta.IsSuccessStatusCode) { Mostrar($"HTTP {(int)respuesta.StatusCode}: {await FabricaControles.Detalle(respuesta)}", true); return; }
            Mostrar($"HTTP {(int)respuesta.StatusCode}: comprador creado correctamente.");
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException) { Mostrar("No se pudo conectar con FastAPI mediante NGINX.", true); }
        finally { guardar.Enabled = true; }
    }
    private void Mostrar(string texto, bool error = false) { estado.ForeColor = error ? Color.Firebrick : Color.DarkGreen; estado.Text = texto; }
}

public sealed class FormVentas : Form
{
    private readonly string token;
    private readonly DataGridView grilla = new() { Dock = DockStyle.Fill, ReadOnly = true, AllowUserToAddRows = false, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill };
    private readonly Label estado = new() { Dock = DockStyle.Bottom, Height = 34, Padding = new Padding(8) };
    public FormVentas(string token)
    {
        this.token = token; Text = "P06 - Listar ventas"; Width = 1000; Height = 570; StartPosition = FormStartPosition.CenterParent;
        Controls.Add(grilla); Controls.Add(estado); Shown += async (_, _) => await Cargar();
    }
    private async Task Cargar()
    {
        estado.Text = "Consultando GET /api/ventas...";
        try
        {
            using var solicitud = FabricaControles.Solicitud(HttpMethod.Get, "api/ventas", token);
            using var respuesta = await FormPrincipal.ClienteHttp.SendAsync(solicitud);
            if (!respuesta.IsSuccessStatusCode) { Mostrar($"HTTP {(int)respuesta.StatusCode}: {await FabricaControles.Detalle(respuesta)}", true); return; }
            var ventas = await respuesta.Content.ReadFromJsonAsync<List<Venta>>() ?? new();
            grilla.DataSource = ventas; Mostrar($"HTTP 200: total de ventas: {ventas.Count}.");
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException or JsonException) { Mostrar("No se pudo obtener el listado de ventas.", true); }
    }
    private void Mostrar(string texto, bool error = false) { estado.ForeColor = error ? Color.Firebrick : Color.DarkGreen; estado.Text = texto; }
}

public sealed class FormCompradores : Form
{
    private readonly string token;
    private readonly DataGridView grilla = new()
    {
        Dock = DockStyle.Fill,
        ReadOnly = true,
        AllowUserToAddRows = false,
        AllowUserToDeleteRows = false,
        RowHeadersVisible = false,
        SelectionMode = DataGridViewSelectionMode.FullRowSelect,
        AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
        BackgroundColor = Color.White
    };
    private readonly Label estado = new()
    {
        Dock = DockStyle.Bottom,
        Height = 36,
        Padding = new Padding(8),
        ForeColor = Color.FromArgb(50, 64, 76)
    };

    public FormCompradores(string token)
    {
        this.token = token;
        Text = "P05 - Listar compradores";
        Width = 900;
        Height = 540;
        StartPosition = FormStartPosition.CenterParent;
        Controls.Add(grilla);
        Controls.Add(estado);
        Shown += async (_, _) => await Cargar();
    }

    private async Task Cargar()
    {
        estado.Text = "Consultando GET /api/compradores...";
        try
        {
            using var solicitud = FabricaControles.Solicitud(HttpMethod.Get, "api/compradores", token);
            using var respuesta = await FormPrincipal.ClienteHttp.SendAsync(solicitud);
            if (!respuesta.IsSuccessStatusCode)
            {
                Mostrar($"HTTP {(int)respuesta.StatusCode}: {await FabricaControles.Detalle(respuesta)}", true);
                return;
            }

            var compradores = await respuesta.Content.ReadFromJsonAsync<List<Comprador>>() ?? new();
            grilla.DataSource = compradores;
            Mostrar($"HTTP 200: total de compradores: {compradores.Count}.");
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException or JsonException)
        {
            Mostrar("No se pudo obtener el listado de compradores.", true);
        }
    }

    private void Mostrar(string texto, bool error = false)
    {
        estado.ForeColor = error ? Color.Firebrick : Color.DarkGreen;
        estado.Text = texto;
    }
}

public sealed class Comprador
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("documento")] public string Documento { get; set; } = "";
    [JsonPropertyName("nombre")] public string Nombre { get; set; } = "";
    [JsonPropertyName("correo")] public string Correo { get; set; } = "";
}

public sealed class Venta
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("operacionId")] public string OperacionId { get; set; } = "";
    [JsonPropertyName("compradorId")] public int CompradorId { get; set; }
    [JsonPropertyName("vehiculoId")] public int VehiculoId { get; set; }
    [JsonPropertyName("estado")] public string Estado { get; set; } = "";
    [JsonPropertyName("precioAcordado")] public decimal? PrecioAcordado { get; set; }
    [JsonPropertyName("moneda")] public string? Moneda { get; set; }
    [JsonPropertyName("fecha")] public string? Fecha { get; set; }
}
