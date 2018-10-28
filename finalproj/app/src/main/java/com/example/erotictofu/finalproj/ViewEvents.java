package com.example.erotictofu.finalproj;

import android.app.PendingIntent;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.format.DateUtils;
import android.view.View;
import android.view.textclassifier.TextLinks;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.SimpleAdapter;
import android.widget.Spinner;

import net.openid.appauth.AuthState;
import net.openid.appauth.AuthorizationException;
import net.openid.appauth.AuthorizationRequest;
import net.openid.appauth.AuthorizationService;
import net.openid.appauth.AuthorizationServiceConfiguration;
import net.openid.appauth.ResponseTypeValues;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.HttpUrl;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

//code based on lecture notes https://gist.github.com/wolfordj/29353e87cebd97fe1cf13c1ae4b3c7fb


public class ViewEvents extends AppCompatActivity  {

    private AuthorizationService mAuthorizationService;
    private AuthState mAuthState;
    private OkHttpClient mOkHttpClient;
    public static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    String primaryCalendarID = null;
    Spinner mDeckUsed;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        SharedPreferences authPreference = getSharedPreferences("auth", MODE_PRIVATE);
        setContentView(R.layout.activity_viewevents);
        mAuthorizationService = new AuthorizationService(this);

        //spinner stuff goes here
        mDeckUsed = (Spinner)findViewById(R.id.deckUsed);
        loadSpinnerData();


        //Display Events Section
        ((Button)findViewById(R.id.getEventsList_button)).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    mAuthState.performActionWithFreshTokens(mAuthorizationService, new AuthState.AuthStateAction() {
                        @Override
                        public void execute (@Nullable String accessToken, @Nullable String idToken, @Nullable AuthorizationException e){
                        if (e == null) {
                            mOkHttpClient = new OkHttpClient();
                            HttpUrl reqUrl = HttpUrl.parse("https://www.googleapis.com/calendar/v3/calendars/primary/events");
                            reqUrl = reqUrl.newBuilder().addQueryParameter("key", "AIzaSyCkwLutoZV9UFTopXg_Ffq328MvLsjHIOY").build();
                            Request request = new Request.Builder()
                                    .url(reqUrl)
                                    .addHeader("Authorization", "Bearer " + accessToken)
                                    .build();
                            mOkHttpClient.newCall(request).enqueue(new Callback() {
                                @Override
                                public void onFailure(Call call, IOException e) {
                                    e.printStackTrace();
                                }

                                /*
                                @Override
                                public void onResponse(Call call, Response response) throws IOException {
                                    String res = response.body().string();
                                    try {
                                        JSONObject j = new JSONObject(res);
                                        JSONArray calendarList = j.getJSONArray("items");
                                        //if at least one calendar exits, get the id and get the events
                                        if (calendarList.length() >= 1) {
                                            JSONObject item = calendarList.getJSONObject(0);
                                            primaryCalendarID = item.getString("id");
                                        }
                                    } catch (JSONException e1) {
                                        e1.printStackTrace();
                                    }
                                }
                                */

                                @Override
                                public void onResponse(Call call, Response response) throws IOException {
                                    String res = response.body().string();
                                    try {
                                        JSONObject j = new JSONObject(res);
                                        JSONArray items = j.getJSONArray("items");
                                        List<Map<String,String>> eventsMap = new ArrayList<Map<String,String>>();
                                        for (int i = 0; i < items.length(); i++) {
                                            //if (j.has("items") == true) {
                                                JSONObject startDateArray = items.getJSONObject(i).getJSONObject("start");
                                                String startDate = null;
                                                if (startDateArray.has("dateTime")) {
                                                    startDate = startDateArray.getString("dateTime");
                                                }
                                                else if (startDateArray.has("date")) {
                                                    startDate = startDateArray.getString("date");
                                                }

                                                String tempDate = startDate.substring(0, 10);
                                                DateFormat df = new SimpleDateFormat("yyyy-MM-dd");
                                                Date checkDate = null;
                                                Date checkAgainst = null;
                                                String dateHolder = "2018-08-11";
                                                try {
                                                    checkDate = df.parse(tempDate);
                                                    checkAgainst = df.parse(dateHolder);
                                                }catch (ParseException ett) {
                                                    ett.printStackTrace();
                                                }
                                                if (checkDate.compareTo(checkAgainst) > 0) {
                                                    String description = items.getJSONObject(i).getString("description");
                                                    String summary = items.getJSONObject(i).getString("summary");
                                                    HashMap<String, String> m = new HashMap<String, String>();
                                                    m.put("TournamentDate", startDate);
                                                    m.put("TournamentName", description);
                                                    m.put("DeckUsed", summary);
                                                    eventsMap.add(m);
                                                }
                                            //}
                                        }

                                        final SimpleAdapter resultsAdapter = new SimpleAdapter(
                                                ViewEvents.this,
                                                eventsMap,
                                                R.layout.calender_item,
                                                new String[]{"TournamentDate", "TournamentName", "DeckUsed"},
                                                new int[]{R.id.tourney_description_text, R.id.date_text, R.id.deckUsed});
                                        runOnUiThread(new Runnable() {
                                            @Override
                                            public void run() {
                                                ((ListView) findViewById(R.id.events_listing)).setAdapter(resultsAdapter);
                                            }
                                        });
                                    } catch (JSONException e1) {
                                        e1.printStackTrace();
                                    }
                                }


                            });

                            /*
                            if (primaryCalendarID != null) {
                                reqUrl = null;
                                reqUrl = HttpUrl.parse("https://www.googleapis.com/calendar/v3/calendars/primary/events");
                                reqUrl = reqUrl.newBuilder().addQueryParameter("key", "AIzaSyCkwLutoZV9UFTopXg_Ffq328MvLsjHIOY").build();
                                request = new Request.Builder()
                                        .url(reqUrl)
                                        .addHeader("Authorization", "Bearer " + accessToken)
                                        .build();
                                mOkHttpClient.newCall(request).enqueue(new Callback() {
                                    @Override
                                    public void onFailure(Call call, IOException e) {
                                        e.printStackTrace();
                                    }

                                    @Override
                                    public void onResponse(Call call, Response response) throws IOException {
                                        String res = response.body().string();
                                        try {
                                            JSONObject j = new JSONObject(res);
                                            JSONArray items = j.getJSONArray("items");
                                            List<Map<String,String>> eventsMap = new ArrayList<Map<String,String>>();
                                            for (int i = 0; i < j.length(); i++) {
                                                JSONArray startDateArray = items.getJSONObject(i).getJSONArray("start");
                                                String startDate = startDateArray.getJSONObject(0).getString("date");
                                                String description = items.getJSONObject(i).getString("description");
                                                String summary = items.getJSONObject(i).getString("summary");
                                                HashMap<String, String> m = new HashMap<String, String>();
                                                m.put("TournamentDate", startDate);
                                                m.put("TournamentName", description);
                                                m.put("DeckUsed", summary);
                                                eventsMap.add(m);
                                            }

                                            final SimpleAdapter postAdapter = new SimpleAdapter(
                                                    ViewEvents.this,
                                                    eventsMap,
                                                    R.layout.calender_item,
                                                    new String[]{"Tournament Description", "date"},
                                                    new int[]{R.id.tourney_description_text, R.id.date_text});
                                            runOnUiThread(new Runnable() {
                                                @Override
                                                public void run() {
                                                    ((ListView) findViewById(R.id.events_listing)).setAdapter(postAdapter);
                                                }
                                            });
                                        } catch (JSONException e1) {
                                            e1.printStackTrace();
                                        }
                                    }

                                });

                            }
                            */
                        }
                        }
                    });
                } catch(Exception e) {
                    e.printStackTrace();
                }
            }
        });

        //Add Event Entry Section
        ((Button)findViewById(R.id.addEntry)).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    mAuthState.performActionWithFreshTokens(mAuthorizationService, new AuthState.AuthStateAction() {
                        @Override
                        public void execute (@Nullable String accessToken, @Nullable String idToken, @Nullable AuthorizationException e){
                           if (e == null) {
                               EditText mTourneyName;

                               mTourneyName = (EditText)findViewById(R.id.eventName);


                               String deckUsed = mDeckUsed.getSelectedItem().toString();
                               String tourneyName = mTourneyName.getText().toString();

                               String currentDate = new SimpleDateFormat("yyyy-MM-dd'T'hh:mm:ss.SSS'Z'").format(new Date());
                               Calendar cal = Calendar.getInstance();
                               cal.setTime(new Date());
                               cal.add(Calendar.HOUR_OF_DAY, 1);
                               String oneHourAhead = new SimpleDateFormat("yyyy-MM-dd'T'hh:mm:ss.SSS'Z'").format(cal.getTime());
                               String json = "{ 'summary' : " + "'" + tourneyName + "'," +
                                       "'description' : " + "'" + deckUsed + "'," +
                                       "'start': {" +
                                            "'dateTime' :" + "'" + currentDate + "', 'timeZone' : 'America/Los_Angeles'}," +
                                       "'end' : {" +
                                            " 'dateTime' :" + "'" + oneHourAhead + "', 'timeZone': 'America/Los_Angeles'}" +
                                       "}";
                               mOkHttpClient = new OkHttpClient();
                               HttpUrl reqUrl = HttpUrl.parse("https://www.googleapis.com/calendar/v3/calendars/primary/events");
                               reqUrl = reqUrl.newBuilder().addQueryParameter("key", "AIzaSyCkwLutoZV9UFTopXg_Ffq328MvLsjHIOY").build();
                               RequestBody body = RequestBody.create(JSON, json);
                               Request request = new Request.Builder()
                                       .url(reqUrl)
                                       .post(body)
                                       .addHeader("Authorization", "Bearer " + accessToken)
                                       .build();
                               mOkHttpClient.newCall(request).enqueue(new Callback() {
                                   @Override
                                   public void onFailure(Call call, IOException e) {
                                       e.printStackTrace();
                                   }

                                   @Override
                                   public void onResponse(Call call, Response response) throws IOException {
                                       String r = response.body().string();
                                   }
                               });
                           }
                       }
                    });
                }catch(Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }



    @Override
    protected void onStart(){
        mAuthState = this.getOrCreateAuthState();
        super.onStart();

    }

    AuthState getOrCreateAuthState(){
        AuthState auth = null;
        SharedPreferences authPreference = getSharedPreferences("auth", MODE_PRIVATE);
        String stateJson = authPreference.getString("stateJson", null);
        if(stateJson != null){
            try {
                auth = AuthState.jsonDeserialize(stateJson);
            } catch (JSONException e) {
                e.printStackTrace();
                return null;
            }
        }
        if( auth != null && auth.getAccessToken() != null){
            return auth;
        } else {
            updateAuthState();
            return null;
        }
    }

    void updateAuthState(){

        Uri authEndpoint = new Uri.Builder().scheme("https").authority("accounts.google.com").path("/o/oauth2/v2/auth").build();
        Uri tokenEndpoint = new Uri.Builder().scheme("https").authority("www.googleapis.com").path("/oauth2/v4/token").build();
        Uri redirect = new Uri.Builder().scheme("com.example.erotictofu.finalproj").path("foo").build();

        AuthorizationServiceConfiguration config = new AuthorizationServiceConfiguration(authEndpoint, tokenEndpoint, null);
        AuthorizationRequest req = new AuthorizationRequest.Builder(config, "324869469603-i2v0oj5bufk04j37r8vq99gk6kuhp7il.apps.googleusercontent.com", ResponseTypeValues.CODE, redirect)
                .setScopes("https://www.googleapis.com/auth/calendar")
                .build();

        Intent authComplete = new Intent(this, AuthCompleteActivity.class);
        mAuthorizationService.performAuthorizationRequest(req, PendingIntent.getActivity(this, req.hashCode(), authComplete, 0));
    }

    private void loadSpinnerData() {

        // Spinner Drop down elements
        List<String> lables = DatabaseHelper.getInstance(getApplicationContext()).getAllDecks();;

        // Creating adapter for spinner
        ArrayAdapter<String> dataAdapter = new ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_item, lables);

        // Drop down layout style - list view with radio button
        dataAdapter
                .setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);

        // attaching data adapter to spinner
        mDeckUsed.setAdapter(dataAdapter);
    }


}
