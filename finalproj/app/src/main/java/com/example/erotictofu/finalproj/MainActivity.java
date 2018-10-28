package com.example.erotictofu.finalproj;

import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import net.openid.appauth.AuthState;
import net.openid.appauth.AuthorizationException;
import net.openid.appauth.AuthorizationResponse;
import net.openid.appauth.AuthorizationService;
import net.openid.appauth.TokenResponse;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button addEvent_Button = (Button) findViewById(R.id.deckDB_button);
        addEvent_Button.setOnClickListener(this);

        Button viewEvents_Button = (Button) findViewById(R.id.gotoViewEvents_button);
        viewEvents_Button.setOnClickListener(this);


    }

    @Override
    public void onClick(View view) {
        Intent i;
        switch(view.getId()) {
            case R.id.deckDB_button:
                i = new Intent(this, DecksActivity.class);
                startActivity(i);
                break;
            case R.id.gotoViewEvents_button:
                i = new Intent(this, ViewEvents.class);
                startActivity(i);
                break;
            default:
                break;
        }
    }

}
