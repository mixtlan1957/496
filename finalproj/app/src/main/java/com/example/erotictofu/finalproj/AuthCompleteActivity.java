package com.example.erotictofu.finalproj;

import android.app.PendingIntent;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;

import net.openid.appauth.AuthState;
import net.openid.appauth.AuthorizationException;
import net.openid.appauth.AuthorizationRequest;
import net.openid.appauth.AuthorizationResponse;
import net.openid.appauth.AuthorizationService;
import net.openid.appauth.AuthorizationServiceConfiguration;
import net.openid.appauth.ResponseTypeValues;
import net.openid.appauth.TokenRequest;
import net.openid.appauth.TokenResponse;

import java.util.HashMap;

//Code based on lecture examples provided at:
// https://gist.github.com/wolfordj/29353e87cebd97fe1cf13c1ae4b3c7fb


public class AuthCompleteActivity extends AppCompatActivity {

    private AuthorizationService mAuthorizationService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_auth_complete);

        mAuthorizationService = new AuthorizationService(this);
        Uri redirectUri = getIntent().getData();
        AuthorizationResponse resp = AuthorizationResponse.fromIntent(getIntent());
        AuthorizationException ex = AuthorizationException.fromIntent(getIntent());

        if(resp != null){
            final AuthState authState = new AuthState(resp, ex);
            mAuthorizationService.performTokenRequest(resp.createTokenExchangeRequest(),
                    new AuthorizationService.TokenResponseCallback() {
                        @Override
                        public void onTokenRequestCompleted(@Nullable TokenResponse tokenResponse, @Nullable AuthorizationException e) {
                            authState.update(tokenResponse,e);
                            SharedPreferences authPreferences = getSharedPreferences("auth", MODE_PRIVATE);
                            authPreferences.edit().putString("stateJson", authState.jsonSerializeString()).apply();
                            finish();
                        }
                    });
        }
        Intent i;
        i = new Intent(this,ViewEvents.class);
        startActivity(i);
    }
}
