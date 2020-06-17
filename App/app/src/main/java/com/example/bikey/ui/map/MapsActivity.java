package com.example.bikey.ui.map;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.example.bikey.R;
import com.example.bikey.bluetooth.CommunicationsTask;
import com.example.bikey.ui.bluetooth.DeviceListActivity;
import com.example.bikey.ui.login.LoginActivity;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

public class MapsActivity extends AppCompatActivity implements OnMapReadyCallback {

    private String time;
    private String velocity;
    private String response;
    private LatLng location;
    private boolean connected;
    private GoogleMap mMap;

    private TextView mServerReplyTime;
    private TextView mServerReplyVelocity;
    private Button btnLockButton;

    protected CommunicationsTask mBluetoothConnection;

    private long interval= 2000;

    private static final String TAG = "ServerResṕonse";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maps);

        Intent newint = getIntent();
        final Intent logout = new Intent(this, LoginActivity.class);
        String mDeviceAddress = newint.getStringExtra(DeviceListActivity.EXTRA_ADDRESS);

        // Create a connection to this device
        mBluetoothConnection = new CommunicationsTask(this, mDeviceAddress);
        mBluetoothConnection.execute();

        mServerReplyTime = findViewById(R.id.serverReplyTime);
        mServerReplyVelocity = findViewById(R.id.serverReplyVelocity);
        btnLockButton = findViewById(R.id.lockButton);

        btnLockButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                lockerBike('b');
                mBluetoothConnection.disconnect();

                startActivity(logout);
            }
        });

        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);

        location = new LatLng(-30.979637, -64.0992437); // Jesús María
        time = "00:00:00";
        velocity = "0.0 km/h";
        connected = false;

        mServerReplyTime.setText(time);
        mServerReplyVelocity.setText(velocity);
    }

    protected void onStart() {
        super.onStart();
        new CountDownTimer(Long.MAX_VALUE, interval) {

            public void onTick(long millisUntilFinished) {
                if (mBluetoothConnection.getStatus() == AsyncTask.Status.FINISHED) {
                    // Espero hasta que establezca la conexión el hilo background CommunicationsTask
                    if (!connected) {
                        lockerBike('u');
                        connected = true;
                    }
                    response = requestData();
                    // Solo actualizo los datos cuando no recibo un string vacío
                    if (!response.isEmpty()) {
                        loadData(response.split(","));
                        updateData();
                    }
                }
            }

            public void onFinish() {

            }
        }.start();
    }

    /**
     * Función para pedir datos al servidor
     * Envía el caracter "g" para solicitar los datos
     * @return cadena de caracteres con la respuesta del servidor
     */
    private String requestData() {
        StringBuilder response = new StringBuilder();
        mBluetoothConnection.write((byte) 'g');
        while (mBluetoothConnection.available() > 0) {

            char c = (char) mBluetoothConnection.read();
            if (c != '$') {
                response.append(c);
            } else {
                // Corto el while cuando recibo el $ para no concatenar response
                break;
            }
        }
        Log.d(TAG, "ServerResponse: " + response);
        return response.toString();
    }

    /**
     * Función para cargar los datos a las variables globales utilizadas en la Activity
     * @param array este array tiene los 3 parámetros recibidos del servidor
     */
    private void loadData(String[] array) {
        time = array[0];
        location = new LatLng(Double.parseDouble(array[1]), Double.parseDouble(array[2]));
        velocity = array[3] + "km/h";
    }

    /**
     * Función para actualizar la vista
     */
    private void updateData() {
        mServerReplyTime.setText(time);
        mServerReplyVelocity.setText(velocity);
        mMap.clear();
        mMap.addMarker(new MarkerOptions().position(location).title("My position"));
        mMap.moveCamera(CameraUpdateFactory.newLatLng(location));
    }

    /**
     * Función para manejar el bloqueador
     * @param c en caso de c = 'b' para bloquear, y en caso de 'u' para desbloquear
     */
    private void lockerBike(char c) {
        mBluetoothConnection.write((byte) c);
        while (mBluetoothConnection.available() > 0) {
            if ((char) mBluetoothConnection.read() == '$') {
                break;
            }
        }
    }

    /**
     * Manipulates the map once available.
     * This callback is triggered when the map is ready to be used.
     * This is where we can add markers or lines, add listeners or move the camera. In this case,
     * we just add a marker near Sydney, Australia.
     * If Google Play services is not installed on the device, the user will be prompted to install
     * it inside the SupportMapFragment. This method will only be triggered once the user has
     * installed Google Play services and returned to the app.
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
        mMap.addMarker(new MarkerOptions().position(location).title("My positiom"));
        mMap.moveCamera(CameraUpdateFactory.newLatLng(location));

        mMap.animateCamera(CameraUpdateFactory.newLatLngZoom(location, 16.0f));
    }
}
