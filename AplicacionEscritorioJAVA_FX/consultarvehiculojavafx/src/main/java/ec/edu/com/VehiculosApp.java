package ec.edu.com;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.beans.property.ReadOnlyObjectWrapper;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.stage.Stage;

import java.io.File;
import java.lang.reflect.Field;
import java.util.function.Function;

//venta equivale a FormPrincipal de windows forms.
public final class VehiculosApp extends Application{

    private final VehiculosApiClient api = new VehiculosApiClient();
    private final PasswordField txtToken = new PasswordField();
    private final Button btnConsultar = new Button("Consultar");
    private final Label lblEstado = new Label("Listoo");
    private final Label lblTotal = new Label("Total de vehiculos: 0");
    private final TableView<Vehiculo> tabla = new TableView<>();

    @Override 
    public void start(Stage ventana){
        Label titulo = new Label("Ventana Vehiculos Registrados");
        txtToken.setPromptText("aki va el jwt");
        txtToken.setMaxWidth(Double.MAX_VALUE);
        btnConsultar.setMaxWidth(130);
        btnConsultar.setOnAction(evento -> consultar());
        HBox acciones = new HBox(14, btnConsultar, lblEstado);
        acciones.setAlignment(Pos.CENTER_LEFT);
        lblEstado.setWrapText(true);

        //grid 
        agregarColumna("ID", Vehiculo::idVehiculo,65);
        agregarColumna("Marca", Vehiculo::marca,119);
        agregarColumna("Modelo", Vehiculo::modelo,135);
        agregarColumna("Placa", Vehiculo::placa,105);
        agregarColumna("Chasis", Vehiculo::chasis,165);
        agregarColumna("Anio", Vehiculo::anio,75);
        agregarColumna("Color", Vehiculo::color,105);
        agregarColumna("Precio", Vehiculo::precio,100);
        agregarColumna("Estado", Vehiculo::estado,100);

        tabla.setPlaceholder(new Label("no hya vehiculos"));

        
        VBox.setVgrow(tabla,Priority.ALWAYS);
        VBox contenido = new VBox(12,titulo, new Label("jwt del usuario:") ,txtToken, acciones, tabla, lblTotal);
        contenido.setPadding(new Insets(22));
        contenido.setStyle("-fx-background-color: green");
        ventana.setScene(new Scene(contenido, 1024,650));
        ventana.setTitle("Consulta Vehiculos");
        ventana.show();
        //mvn clean javafx:run
    }

    private void consultar(){


        String jwt = txtToken.getText().trim();

        if(jwt.regionMatches(true, 0, "Bearer ",0,7)){

            jwt = jwt.substring(7).trim();

        }

        btnConsultar.setDisable(true);

        mostrarEstado("consultandooo... api java", false);

        api.consultarVehiculos(jwt).whenComplete((resultado, error) ->

            Platform.runLater(() -> {
                
                btnConsultar.setDisable(false);

                if (error != null) {
                    mostrarEstado("no se conecto con jaba", true);

                           return;
                }

                if (resultado.codigoHttp() == 401){

                    mostrarEstado("Http 401: jwt vencido no funciona", true);
                }else if (resultado.codigoHttp()==403){
                    mostrarEstado("http 403: usuauro no tiene acceso al servidor", true);
                } else {
                    tabla.getItems().setAll(resultado.vehiculos());

                    lblTotal.setText("total de vehiculos" + resultado.vehiculos().size());

                }

                         })
        );

    }
    private void mostrarEstado(String texto, boolean error){
        lblEstado.setText(texto);
        lblEstado.setTextFill(error? Color.RED : Color.BLUE);
    }
    private <T> void agregarColumna(

        String titulo,
        Function<Vehiculo, T> valor,
        double ancho){

    TableColumn<Vehiculo, T> columna = new TableColumn<>(titulo);

    columna.setCellValueFactory(fila -> new ReadOnlyObjectWrapper<>(valor.apply(fila.getValue())));
    columna.setPrefWidth(ancho);
    tabla.getColumns().add(columna);

        

    }

}