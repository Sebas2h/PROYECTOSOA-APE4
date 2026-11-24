#nullable enable

namespace ConsultaVehiculosWinForms;

partial class FormPrincipal
{
    private System.ComponentModel.IContainer? components = null;
    private Label lblTitulo = null!;
    private Label lblSubtitulo = null!;
    private Label lblToken = null!;
    private TextBox txtToken = null!;
    private Button btnConsultar = null!;
    private Button btnCrearVehiculo = null!;
    private Button btnCrearComprador = null!;
    private Button btnListarCompradores = null!;
    private Button btnListarVentas = null!;
    private Label lblEstado = null!;
    private Label lblTotal = null!;
    private DataGridView dgvVehiculos = null!;

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            components?.Dispose();
        }
        base.Dispose(disposing);
    }

    private void InitializeComponent()
    {
        DataGridViewCellStyle dataGridViewCellStyle1 = new DataGridViewCellStyle();
        lblTitulo = new Label();
        lblSubtitulo = new Label();
        lblToken = new Label();
        txtToken = new TextBox();
        btnConsultar = new Button();
        btnCrearVehiculo = new Button();
        btnCrearComprador = new Button();
        btnListarCompradores = new Button();
        btnListarVentas = new Button();
        lblEstado = new Label();
        lblTotal = new Label();
        dgvVehiculos = new DataGridView();
        ((System.ComponentModel.ISupportInitialize)dgvVehiculos).BeginInit();
        SuspendLayout();
        // 
        // lblTitulo
        // 
        lblTitulo.AutoSize = true;
        lblTitulo.Font = new Font("Segoe UI", 20F, FontStyle.Bold);
        lblTitulo.ForeColor = Color.FromArgb(31, 41, 55);
        lblTitulo.Location = new Point(28, 21);
        lblTitulo.Name = "lblTitulo";
        lblTitulo.Size = new Size(361, 46);
        lblTitulo.TabIndex = 0;
        lblTitulo.Text = "Vehículos registrados";
        lblTitulo.Click += lblTitulo_Click;
        // 
        // lblSubtitulo
        // 
        lblSubtitulo.AutoSize = true;
        lblSubtitulo.Font = new Font("Segoe UI", 10F);
        lblSubtitulo.ForeColor = Color.FromArgb(90, 97, 108);
        lblSubtitulo.Location = new Point(30, 71);
        lblSubtitulo.Name = "lblSubtitulo";
        lblSubtitulo.Size = new Size(0, 23);
        lblSubtitulo.TabIndex = 1;
        // 
        // lblToken
        // 
        lblToken.AutoSize = true;
        lblToken.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        lblToken.Location = new Point(30, 113);
        lblToken.Name = "lblToken";
        lblToken.Size = new Size(45, 23);
        lblToken.TabIndex = 2;
        lblToken.Text = "JWT";
        // 
        // txtToken
        // 
        txtToken.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
        txtToken.Location = new Point(30, 144);
        txtToken.Name = "txtToken";
        txtToken.Size = new Size(975, 30);
        txtToken.TabIndex = 0;
        txtToken.UseSystemPasswordChar = true;
        txtToken.TextChanged += txtToken_TextChanged;
        // 
        // btnConsultar
        // 
        btnConsultar.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        btnConsultar.Location = new Point(30, 196);
        btnConsultar.Name = "btnConsultar";
        btnConsultar.Size = new Size(155, 42);
        btnConsultar.TabIndex = 1;
        btnConsultar.Text = "Listar vehículos";
        btnConsultar.UseVisualStyleBackColor = true;
        btnConsultar.Click += btnConsultar_Click;
        // 
        // btnCrearVehiculo
        // 
        btnCrearVehiculo.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        btnCrearVehiculo.Location = new Point(195, 196);
        btnCrearVehiculo.Name = "btnCrearVehiculo";
        btnCrearVehiculo.Size = new Size(170, 42);
        btnCrearVehiculo.Text = "Crear vehículo";
        btnCrearVehiculo.UseVisualStyleBackColor = true;
        btnCrearVehiculo.Click += btnCrearVehiculo_Click;
        // 
        // btnCrearComprador
        // 
        btnCrearComprador.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        btnCrearComprador.Location = new Point(375, 196);
        btnCrearComprador.Name = "btnCrearComprador";
        btnCrearComprador.Size = new Size(185, 42);
        btnCrearComprador.Text = "Crear comprador";
        btnCrearComprador.UseVisualStyleBackColor = true;
        btnCrearComprador.Click += btnCrearComprador_Click;
        // 
        // btnListarCompradores
        // 
        btnListarCompradores.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        btnListarCompradores.Location = new Point(570, 196);
        btnListarCompradores.Name = "btnListarCompradores";
        btnListarCompradores.Size = new Size(205, 42);
        btnListarCompradores.Text = "Listar compradores";
        btnListarCompradores.UseVisualStyleBackColor = true;
        btnListarCompradores.Click += btnListarCompradores_Click;
        // 
        // btnListarVentas
        // 
        btnListarVentas.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        btnListarVentas.Location = new Point(785, 196);
        btnListarVentas.Name = "btnListarVentas";
        btnListarVentas.Size = new Size(155, 42);
        btnListarVentas.Text = "Listar ventas";
        btnListarVentas.UseVisualStyleBackColor = true;
        btnListarVentas.Click += btnListarVentas_Click;
        // 
        // lblEstado
        // 
        lblEstado.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
        lblEstado.Font = new Font("Segoe UI", 9F);
        lblEstado.ForeColor = Color.FromArgb(50, 64, 76);
        lblEstado.Location = new Point(30, 242);
        lblEstado.Name = "lblEstado";
        lblEstado.Size = new Size(975, 30);
        lblEstado.TabIndex = 3;
        lblEstado.Text = "Bandera";
        lblEstado.TextAlign = ContentAlignment.MiddleLeft;
        // 
        // lblTotal
        // 
        lblTotal.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
        lblTotal.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        lblTotal.Location = new Point(30, 626);
        lblTotal.Name = "lblTotal";
        lblTotal.Size = new Size(975, 30);
        lblTotal.TabIndex = 4;
        lblTotal.Text = "Total de vehículos: 0";
        // 
        // dgvVehiculos
        // 
        dgvVehiculos.AllowUserToAddRows = false;
        dgvVehiculos.AllowUserToDeleteRows = false;
        dataGridViewCellStyle1.BackColor = Color.FromArgb(245, 247, 250);
        dgvVehiculos.AlternatingRowsDefaultCellStyle = dataGridViewCellStyle1;
        dgvVehiculos.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
        dgvVehiculos.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
        dgvVehiculos.BackgroundColor = Color.White;
        dgvVehiculos.ColumnHeadersHeight = 38;
        dgvVehiculos.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing;
        dgvVehiculos.Location = new Point(30, 282);
        dgvVehiculos.MultiSelect = false;
        dgvVehiculos.Name = "dgvVehiculos";
        dgvVehiculos.ReadOnly = true;
        dgvVehiculos.RowHeadersVisible = false;
        dgvVehiculos.RowHeadersWidth = 51;
        dgvVehiculos.RowTemplate.Height = 30;
        dgvVehiculos.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
        dgvVehiculos.Size = new Size(975, 332);
        dgvVehiculos.TabIndex = 2;
        // 
        // FormPrincipal
        // 
        AutoScaleDimensions = new SizeF(9F, 23F);
        AutoScaleMode = AutoScaleMode.Font;
        BackColor = Color.White;
        ClientSize = new Size(1037, 675);
        Controls.Add(lblTitulo);
        Controls.Add(lblSubtitulo);
        Controls.Add(lblToken);
        Controls.Add(txtToken);
        Controls.Add(btnConsultar);
        Controls.Add(btnCrearVehiculo);
        Controls.Add(btnCrearComprador);
        Controls.Add(btnListarCompradores);
        Controls.Add(btnListarVentas);
        Controls.Add(lblEstado);
        Controls.Add(dgvVehiculos);
        Controls.Add(lblTotal);
        Font = new Font("Segoe UI", 10F);
        MinimumSize = new Size(940, 540);
        Name = "FormPrincipal";
        StartPosition = FormStartPosition.CenterScreen;
        Text = "Form1";
        ((System.ComponentModel.ISupportInitialize)dgvVehiculos).EndInit();
        ResumeLayout(false);
        PerformLayout();
    }

    private static DataGridViewTextBoxColumn Columna(
        string encabezado, string propiedad, float peso, string? formato = null)
    {
        var columna = new DataGridViewTextBoxColumn
        {
            HeaderText = encabezado,
            DataPropertyName = propiedad,
            Name = "col" + propiedad,
            FillWeight = peso,
            ReadOnly = true,
            SortMode = DataGridViewColumnSortMode.Automatic
        };
        if (formato is not null)
        {
            columna.DefaultCellStyle.Format = formato;
            columna.DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
        }
        return columna;
    }
}
